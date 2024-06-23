from celery.result import AsyncResult
import asyncio
from .celery_config import celery_app
from .bots.trading_bot import run_bot

@celery_app.task(name="execute_trade")
def execute_trade(user_id, api_key, api_secret, ticker, quantity, timeframe, demo):

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot(user_id, api_key, api_secret, ticker, quantity, timeframe, demo))

@celery_app.task(name="stop_trade")
def stop_trade(task_id):

    loop = asyncio.get_event_loop()
    loop.run_until_complete(stop_task(task_id))

def stop_task(task_id: str):

    task_result = AsyncResult(task_id)
    if task_result:
        task_result.revoke(terminate=True)