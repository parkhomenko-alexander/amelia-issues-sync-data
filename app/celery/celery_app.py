from celery import Celery
from celery.schedules import crontab
from config import config

celery_app = Celery(
    __name__,
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    include=["amelia_organizations_tasks"],
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
)



celery_app.conf.beat_schedule = {
    "get_facilities": {
        "task": "amelia_organizations_tasks.sync_ficilities", 
        "schedule": crontab(minute="*/2"),
        # "schedule": crontab(minute=1, hour="*/20"),
    },
    "get_compnanies": {
        "task": "amelia_organizations_tasks.sync_companies", 
        "schedule": crontab(minute="*/2"),
    },
    "get_priorities": {
        "task": "amelia_organizations_tasks.sync_priorities", 
        "schedule": crontab(minute="*/2"),
    }
}