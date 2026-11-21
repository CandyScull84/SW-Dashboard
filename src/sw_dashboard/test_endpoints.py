# test_endpoints.py

from api.merge_requests import show_active_merge_requests, get_merge_requests_per_person
from api.current_projects import get_recent_push_events, get_active_project_summary
from api.pipelines import get_recent_failing_pipelines
from api.gitlab_client import gitlab
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


print("=== TEST: Merge Requests ===")
mrs = show_active_merge_requests()
print(f"Found {len(mrs)} open merge requests")
for mr in mrs[:5]:
    print(f" - {mr['title']} ({mr['project_id']}) by {mr['author'].get('name')}")

print("\n=== TEST: Merge Requests per Person ===")
mrs_per_person = get_merge_requests_per_person()
for mr in mrs_per_person[:5]:
    print(f" - {mr['author_name']} -> {mr['assignee_name']} | {mr['title']}")

print("\n=== TEST: Recent Push Events ===")
pushes = get_recent_push_events(limit=5)
for p in pushes:
    print(f" - {p['project_name']} | {p['user_name']} | {p['timestamp']} | {p['commit_title']}")

print("\n=== TEST: Active Projects ===")
summary = get_active_project_summary(days=1)
print(f"Active projects: {summary['active_projects']} of {summary['total_projects']}")

print("\n=== TEST: Failing Pipelines ===")
fails = get_recent_failing_pipelines(limit_projects=10, include_subgroups=True)
for f in fails:
    print(f" - {f['project_name']} | {f['status']} | {f['user_name']} | {f['updated_at']}")

data, headers = gitlab.get("/projects", include_headers=True)
print(len(data or []), "projects found")
