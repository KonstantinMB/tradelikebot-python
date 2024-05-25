# tasks.py
from celery_config import celery_app
from bots.trading_bot import run_bot
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def run_trading_bot(self, api_key: str, api_secret: str, ticker: str, order_size: float, timeframe: str, demo: bool):
    try:
        logger.info(f"Starting bot for ticker {ticker}")
        run_bot(api_key, api_secret, ticker, order_size, timeframe, demo)
        logger.info(f"Bot completed for ticker {ticker}")
    except Exception as e:
        logger.error(f"Error running bot for ticker {ticker}: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)
