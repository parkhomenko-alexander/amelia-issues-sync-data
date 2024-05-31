from celery import Celery
from celery.schedules import crontab
from config import config


celery_app = Celery(
    __name__,
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    include=[
        "tasks.issues_tasks.callback",
        "tasks.issues_tasks.orchestrator",
        "tasks.issues_tasks.issues_tasks",

        "tasks.buildings_tasks",
        "tasks.organizations_tasks",
    ],
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
)

celery_app.conf.beat_schedule = {
    # "get_facilities": {
    #     "task": "tasks.amelia_organizations_tasks.sync_ficilities", 
    #     # "schedule": timedelta(days=30),
    #     "schedule": crontab(day_of_month="1", hour="0", minute="0"),
    # },
    # "get_compnanies": {
    #     "task": "tasks.amelia_organizations_tasks.sync_companies", 
    #     "schedule": crontab(day_of_month="1", hour="0", minute="0"),
    # },
    # "get_priorities": {
    #     "task": "tasks.amelia_organizations_tasks.sync_priorities", 
    #     "schedule": crontab(day_of_month="1", hour="0", minute="0"),
    # },
    # "sync_workflows": {
    #     "task": "tasks.amelia_organizations_tasks.sync_workflows", 
    #     "schedule": crontab(day_of_month="1", hour="0", minute="0"),
    # },
    # "sync_users": {
    #     "task": "tasks.amelia_organizations_tasks.sync_users", 
    #     "schedule": crontab(hour="22", minute="0", day_of_month="15")
    # },


    # "sync_buildings": {
    #     "task": "tasks.amelia_buildings_tasks.sync_buildings", 
    #     "schedule": crontab(hour="22", minute="0", day_of_month="15")
    # },
    # "sync_floors": {
    #     "task": "tasks.amelia_buildings_tasks.sync_floors", 
    #     "schedule": crontab(hour="22", minute="0", day_of_month="15")
    # },
    # "sync_rooms": {
    #     "task": "tasks.amelia_buildings_tasks.sync_rooms", 
    #     "schedule": crontab(hour="22", minute="0", day_of_month="15")
    # },
    # "sync_tech_passports": {
    #     "task": "tasks.amelia_buildings_tasks.sync_tech_passports", 
    #     "schedule": crontab(hour="22", minute="0", day_of_month="15")
    # },


    # "sync_statuses": {
    #     "task": "tasks.amelia_issues_tasks.sync_statuses", 
    #     "schedule": crontab(day_of_month="1", hour="0", minute="0")
    # },
    # "sync_services": {
    #     "task": "tasks.amelia_issues_tasks.sync_services", 
    #     "schedule": crontab(day_of_month="1", hour="0", minute="0")
    # },
    # "sync_work_categories": {
    #     "task": "tasks.amelia_issues_tasks.sync_work_categories", 
    #     "schedule": crontab(day_of_month="1", hour="0", minute="0")
    # },
    # "sync_current_issues": {
    #     "task": "tasks.amelia_issues_tasks.sync_current_issues", 
    #     "schedule": crontab(minute="*/50")
    # },

   "sync_current_archive_issues": {
        "task": "tasks.issues_tasks.orchestrator.sync_issues_current_archive_chord_job",
        "schedule": crontab(minute="0", hour='*/3'),
        "kwargs": {"delay": 3, "service_external_ids": [3, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19], "archive_borders": {"start": 1, "end": 30}},
    },
    "sync_current_archive_issues_half": {
        "task": "tasks.issues_tasks.orchestrator.sync_issues_current_archive_chord_job",
        "schedule": crontab(minute="30", hour='1-23/3'),  
        "kwargs": {"delay": 3, "service_external_ids": [3, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19], "archive_borders": {"start": 1, "end": 30}}
    }
}
