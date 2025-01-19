from loguru import logger
from app.celery.celery_app import celery_app


@celery_app.task
def sync_issues_current_archive_chord_job_callback(results: list[str]) -> str:
    msg: str = "Synchronizing issues (current/archive) job completed successfully" 
    logger.info(msg)
    return msg