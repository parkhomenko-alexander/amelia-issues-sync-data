from app.huey.scheduler import patch_common_users, sync_issues_dynamic

res = sync_issues_dynamic(time_range=["2025-01-19T00:00:00Z", "2025-01-22T00:00:00Z"], delay=2.3)
# res = patch_common_users(2, delay=1.5)
