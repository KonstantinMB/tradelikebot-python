# main.py
from celery.app.control import Control
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from .celery_worker import execute_trade, stop_trade
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
from .celery_config import celery_app
from pydantic import BaseModel
from .db.base_repo import MongoDB
from .db.trades_repo import TradeDB
from .db.user_task_repo import UserTaskDB
import os
from cryptography.fernet import Fernet
from .bots.aws_secret import get_secret

logger = logging.getLogger(__name__)

app = FastAPI(
    root_path="/api"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

celery_control = Control(app=celery_app)

mongo_db = MongoDB(str(os.getenv('MONGODB_URI')), "test")
trade_db = TradeDB(mongo_db)
user_task_db = UserTaskDB(mongo_db)

secret_name = os.getenv('SECRET_NAME')
encryption_key = get_secret(secret_name)

def encrypt_data(data, key):
    fernet = Fernet(key)
    return fernet.encrypt(data.encode()).decode()

class TradeLimitException(Exception):
    def __init__(self, name: str):
        self.name = name

@app.exception_handler(TradeLimitException)
async def trade_limit_exception_handler(exc: TradeLimitException):
    return JSONResponse(
        status_code=400,
        content={"message": f"Currently supporting only 1 trade per user. You already have an active trade: {exc.name}"},
    )

class TradeRequest(BaseModel):
    user_id: str
    api_key: str
    api_secret: str
    ticker: str
    quantity: float
    timeframe: str
    demo: bool

class StopRequest(BaseModel):
    user_id: str

class PerformanceData(BaseModel):
    time: str
    balance: float
    profitLoss: float

class User(BaseModel):
    name: str
    email: str
    image: str
    apiKey: str
    apiSecret: str
    demo: bool

class InvestmentStatusRequest(BaseModel):
    user_id: str

@app.post("/bot/status")
async def get_investment_status(request: InvestmentStatusRequest):

    total_investment = await trade_db.get_total_investment_by_user(request.user_id)
    if total_investment is None:
        raise HTTPException(status_code=404, detail="User not found or no trades")
    return {"user_id": request.user_id, "total_investment": total_investment}

@app.post("/bot/trades")
async def trade(request: TradeRequest):

    existing_trade = await trade_db.get_trade_by_user_id(request.user_id)
    if existing_trade:
        raise TradeLimitException(existing_trade['ticker'])

    try:
        logger.info(f"Received trade request: {request.json()}")

        task = execute_trade.delay(
            user_id=request.user_id,
            api_key=encrypt_data(request.api_key, encryption_key),
            api_secret=encrypt_data(request.api_secret, encryption_key),
            ticker=request.ticker,
            quantity=request.quantity,
            timeframe=request.timeframe,
            demo=request.demo
        )

        logger.info(f"Trade initiated for {request.ticker}, task id: {task.id}")
        return {"task_id": task.id}

    except Exception as e:
        logger.error(f"Error processing trade request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bot/stop")
async def stop(request: StopRequest):

    user_id = request.user_id

    # Validate trade exists:
    user_task = await user_task_db.get_user_task_by_user_id(user_id)
    if not user_task:
        raise HTTPException(status_code=404, detail="Task not found in user_task collection")

    # Stop the Celery task
    task_id = user_task["task_id"]
    stop_trade.delay(task_id)
    logger.info(f"Stop trade requested for task id: {task_id}")

    # Fetch the trade associated with the user_id and task_id
    existing_trade = await trade_db.get_trade_by_user_id(user_id)
    if not existing_trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    # Delete the trade from the trade collection
    deleted_count = await trade_db.delete_trade_by_id(existing_trade["_id"])
    if not deleted_count:
        raise HTTPException(status_code=500, detail="Failed to delete trade")

    # Delete the mapping from the user_task collection
    deleted_task_count = await user_task_db.delete_user_task_by_id(user_task["_id"])
    if not deleted_task_count:
        raise HTTPException(status_code=500, detail="Failed to delete user task mapping")

    return {"message": "Trade and task mapping deleted successfully"}

@app.get("/tasks/{task_id}")
def get_status(task_id: str):
    try:
        task_result = AsyncResult(task_id)

        # Extract the result and status
        result = {
            "task_id": task_id,
            "task_status": task_result.status,
            "task_result": task_result.result if task_result.result else "No result available"
        }

        return JSONResponse(result)

    except Exception as e:
        logger.error(f"Error retrieving task status for task_id {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
