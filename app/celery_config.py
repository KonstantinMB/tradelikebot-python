from celery import Celery

celery_app = Celery(
    'trading_tasks',  # This is the name of your Celery app, choose appropriately
    broker='redis://localhost:6379/0',  # Make sure the Redis URL matches your Redis setup
    backend='redis://localhost:6379/0'
)

# Optional: Configure Celery to manage tasks better
celery_app.conf.update(
    broker_connection_retry_on_startup=True,
    task_serializer='json',
    accept_content=['json'],  # Accept only JSON content
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,  # This tells workers to fetch one message at a time
    task_acks_late=True  # Ensures tasks are acknowledged after they're completed
)
