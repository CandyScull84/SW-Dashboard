from api.merge_requests import get_group_merge_requests_page, show_active_merge_requests
from config import GITLAB_GROUP_ID

items, meta = get_group_merge_requests_page(group_id=GITLAB_GROUP_ID, page=1, per_page=5)
print("===Test 1: En sida ===")
print(f"Antal objekt: {len(items)}")
print("Meta:", meta)

print("\n=== Test 2: Alla merge requests ===")
all_items = show_active_merge_requests(group_id=GITLAB_GROUP_ID, debug=True)
print(f"Totalt antal merge requests: {len(all_items)}")