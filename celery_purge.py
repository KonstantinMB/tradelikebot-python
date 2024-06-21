from project.celery_config import celery_app

if __name__ == "__main__":
    print("Purging Celery tasks...")
    purged_count = celery_app.control.purge()
    print(f"Purged {purged_count} tasks.")