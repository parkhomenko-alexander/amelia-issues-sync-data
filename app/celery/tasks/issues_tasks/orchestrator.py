from celery import Task
from typing import cast

from celery import chord
from loguru import logger
from app.celery.amelia_api_calls import Borders
from app.celery.celery_app import celery_app
from app.celery.tasks.issues_tasks.callback import sync_issues_current_archive_chord_job_callback
from app.celery.tasks.issues_tasks.issues_tasks import sync_archive, sync_current_issues
from config import config

@celery_app.task
def sync_issues_current_archive_chord_job(service_external_ids: list[int] = [], current_borders: Borders | None = None, archive_borders: Borders | None = None, delay: float = config.API_CALLS_DELAY):
    try:
        logger.info("Synchronizing issues (current/archive) job is start")
        sync_current_issues_casted_task = cast(Task, sync_current_issues)
        sync_archive_casted_task = cast(Task, sync_archive)
        callback = cast(Task, sync_issues_current_archive_chord_job_callback)
        job = chord([
            sync_current_issues_casted_task.s(delay, service_external_ids, current_borders),
            sync_archive_casted_task.s(delay, service_external_ids, current_borders)
        ])
        result = job(callback.s())
    except Exception as e:
        return f"Failed to enqueue tasks: {e}"