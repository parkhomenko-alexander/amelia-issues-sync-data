from app.huey.huey_app import huey

from huey import crontab

from app.huey.issues_tasks import sync_issues_dynamic
from app.huey.organizations_tasks import patch_common_users
from logger import logger


# @huey.periodic_task(crontab(minute='*/20'))
# def periodic_iss():
#     delay = 2.5
    
#     sync_issues_dynamic(delay=delay)

#     print("Periodic sync task triggered")


@huey.periodic_task(crontab(minute='*/50'))
def periodic_users():
    delay = 1
    pages=3

    patch_common_users(pages=pages, delay=delay)

    logger.info("Periodic users patch task triggered")