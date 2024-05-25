# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bot_tasks import run_trading_bot
import logging

# Import and configure logging
import logging_config  # This ensures the logging configuration is loaded

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.post("/trade")
async def trade(request: TradeRequest):
    task = run_trading_bot.delay(request.api_key, request.api_secret, request.ticker, request.order_size, request.timeframe, request.demo)
    logger.info(f"Trade initiated for {request.ticker}, task id: {task.id}")
    return {"message": f"Trade for {request.ticker} initiated.", "task_id": task.id}

@app.post("/stop")
async def stop_task(request: StopRequest):
    task_id = request.task_id
    task = run_trading_bot.AsyncResult(task_id)
    if task.state not in ['PENDING', 'REVOKED', 'FAILURE']:
        task.revoke(terminate=True)
        logger.info(f"Task {task_id} stopped.")
        return {"message": f"Task {task_id} stopped."}
    else:
        logger.warning(f"Task {task_id} not found or already in terminal state.")
        raise HTTPException(status_code=404, detail="Task not found")

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = run_trading_bot.AsyncResult(task_id)
    return {"task_id": task_id, "state": task.state, "info": task.info}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
