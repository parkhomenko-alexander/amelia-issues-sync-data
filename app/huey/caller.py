from app.huey.scheduler import patch_common_users, sync_issues_dynamic

res = sync_issues_dynamic(issues_id=[151375, 151386, 151857, 151982, 153329, 153330, 153331, 153332, 153333, 153334, 153336, 153337, 153338, 153339, 153340, 153341, 153342, 153343, 153344, 153345, 153346, 153347, 153348, 153349, 153350, 153351, 153352, 153353, 153354, 153355, 153356, 153357]
, delay=2)
res = sync_issues_dynamic(time_range=["2025-01-22T00:00:00Z", "2025-01-27T00:00:00Z"], delay=2)
# res = patch_common_users(2, delay=1.5)
