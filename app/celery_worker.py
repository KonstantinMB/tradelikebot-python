from celery.contrib.abortable import AbortableTask
import asyncio
from .celery_config import celery_app
from .bots.trading_bot import run_bot

@celery_app.task(name="execute_trade", bind=True, base=AbortableTask)
def execute_trade(self, db_created_trade_id, api_key, api_secret, ticker, quantity, timeframe, demo):

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot(self, db_created_trade_id, api_key, api_secret, ticker, quantity, timeframe, demo))


