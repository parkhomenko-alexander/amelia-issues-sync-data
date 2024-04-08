from celery import Celery
from celery.schedules import crontab
from  config import config


celery_app = Celery(
    __name__,
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    include=[
        "tasks.amelia_organizations_tasks",
        "tasks.amelia_buildings_tasks",
        "tasks.amelia_issues_tasks"
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
}
