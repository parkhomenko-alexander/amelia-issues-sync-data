from celery import Celery
from celery.schedules import crontab

from config import config

celery_app = Celery(
    __name__,
    broker=config.get_redis_uri(),
    backend=config.get_redis_uri(),
    include=[
        "tasks.issues_tasks.callback",
        "tasks.issues_tasks.orchestrator",
        "tasks.issues_tasks.issues_tasks",
        "tasks.issues_tasks.dynamic_issues_tasks",

        "tasks.buildings_tasks",
        "tasks.organizations_tasks",

        "tasks.cache_tasks",
    ],
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
)

celery_app.conf.beat_schedule = {
    "sync_dynamic_issues": {
        "task": "tasks.issues_tasks.dynamic_issues_tasks.call_dynamic_issues",
        "schedule": crontab(minute="*/20"),
        "kwargs": {"delay": config.API_CALLS_DELAY, "pages": 600}
    },
    "sync_cache": {
        "task": "tasks.cache_tasks.update_building_cache",
        "schedule": crontab(minute="0", hour="3"),
    },
    # "patch_users": {
    #     "task": "tasks.organizations_tasks.patch_common_users",
    #     "schedule": crontab(hour='*/2', minute="0"),
    #     "kwargs": {"delay": 3, "pages": 4}
    # },
}
