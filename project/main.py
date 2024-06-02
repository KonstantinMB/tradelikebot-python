# main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from celery_worker import execute_trade
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
from typing import List
from celery import Celery
from bots import trading_bot

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

celery = Celery(
    __name__,
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0"
)

class TradeRequest(BaseModel):
    api_key: str
    api_secret: str
    ticker: str
    order_size: float
    timeframe: str
    demo: bool

class StopRequest(BaseModel):
    task_id: str

class PerformanceData(BaseModel):
    time: str
    balance: float
    profitLoss: float

# Mock data
performance_data = [
    PerformanceData(time="2024-05-01T00:00:00Z", balance=1000, profitLoss=0),
    PerformanceData(time="2024-05-02T00:00:00Z", balance=1010, profitLoss=10),
    PerformanceData(time="2024-05-03T00:00:00Z", balance=1005, profitLoss=-5),
    # Add more data points here...
]

@app.post("/trade")
async def trade(request: TradeRequest):

    task = execute_trade.delay(api_key=request.api_key, api_secret=request.api_secret,
                             ticker=request.ticker, order_size=request.order_size,
                             timeframe=request.timeframe, demo=request.demo)
    logger.info(f"Trade initiated for {request.ticker}, task id: {task.id}")
    return {"message": f"Trade for {request.ticker} initiated.", "task_id": task.id}

@celery.task
def run_trading_bot(api_key, api_secret, ticker, order_size, timeframe, demo):

    trading_bot.run_bot(api_key, api_secret, ticker, order_size, timeframe, demo)

    return {"message": f"Trade for {ticker} initiated."}
@app.get("/tasks/{task_id}")
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)

@app.get("/performance", response_model=List[PerformanceData])
async def get_performance():
    return performance_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
