import asyncio
from .bots.trading_bot import run_bot
from .celery_config import celery_app
from celery.app.control import Control

celery_control = Control(app=celery_app)

@celery_app.task(name="execute_trade")
def execute_trade(db_created_trade_id, api_key, api_secret, ticker, quantity, timeframe, demo):

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot(db_created_trade_id, api_key, api_secret, ticker, quantity, timeframe, demo))

@celery_app.task(name="stop_trade")
def stop_trade(task_id):

    loop = asyncio.get_event_loop()
    loop.run_until_complete(stop_task(task_id))

def stop_task(task_id: str):

    celery_control.revoke(task_id, terminate=True)
