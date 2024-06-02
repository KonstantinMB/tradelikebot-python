# celery_config.py
from celery_config import celery_app
from bots.trading_bot import run_bot  # Assuming run_bot is your function to execute trading

@celery_app.task(name="execute_trade")
def execute_trade(api_key, api_secret, ticker, order_size, timeframe, demo):
    """
    Task to execute a trading operation.
    """
    return run_bot(api_key, api_secret, ticker, order_size, timeframe, demo)