### Вызов таски на обновление заявок 
celery -A celery_app call tasks.issues_tasks.dynamic_issues_tasks.call_dynamic_issues --kwargs='{"page":2, "time_range": ["2025-02-19T00:00:00+10:00", "2025-02-19T00:00:00+10:00"], "delay": 2}'

celery -A celery_app call tasks.issues_tasks.dynamic_issues_tasks.call_dynamic_issues --kwargs='{"page":500, "time_range": ["2025-02-21T00:00:00+10:00", "2025-02-25T00:00:00+10:00"], "delay": 2}'

celery -A celery_app call tasks.organizations_tasks.patch_common_users --kwargs='{"pages": 30, "delay": 2}'