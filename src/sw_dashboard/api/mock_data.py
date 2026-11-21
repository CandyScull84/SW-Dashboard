from typing import List, Dict, Any
from datetime import datetime, timezone

# Fictional projects used throughout the demo
MOCK_PROJECTS = [
    {"id": 400, "name": "sw-dashboard"},
    {"id": 405, "name": "auth-service"},
    {"id": 419, "name": "ui-library"},
    {"id": 420, "name": "data-pipeline"},
    {"id": 425, "name": "reporting-tool"},
    {"id": 430, "name": "mobile-app"},
    {"id": 432, "name": "legacy-api"},
    {"id": 435, "name": "notification-service"},
    {"id": 440, "name": "admin-portal"},
    {"id": 445, "name": "test-automation"},
]

# Fictional team members used throughout the demo
MOCK_USERS = [
    {"name": "Alice", "username": "alice123"},
    {"name": "Bob", "username": "bob456"},
    {"name": "Charlie", "username": "charlie789"},
    {"name": "Diana", "username": "diana123"},
    {"name": "Elias", "username": "elias123"},
    {"name": "Fatima", "username": "fatima123"},
    {"name": "Gustav", "username": "gustav123"},
    {"name": "Hanna", "username": "hanna123"},
]


def mock_push_events() -> List[Dict[str, Any]]:
    today = datetime.now().strftime("%Y-%m-%d")

    events = [
        (400, "Alice", "Improve dashboard layout", "09:10:00"),
        (405, "Bob", "Add OAuth provider", "09:05:00"),
        (419, "Diana", "Refactor button styles", "08:30:00"),
        (420, "Charlie", "Fix data processing error", "08:15:00"),
        (425, "Elias", "Add monthly report", "08:00:00"),
        (400, "Alice", "Update API integration", "07:55:00"),
        (430, "Gustav", "Fix navigation issue", "07:40:00"),
        (435, "Hanna", "Improve email retries", "07:30:00"),
        (405, "Bob", "Update authentication tests", "07:20:00"),
        (440, "Fatima", "Add user permissions", "07:10:00"),
        (445, "Charlie", "Improve test coverage", "07:00:00"),
        (432, "Diana", "Fix deprecated endpoint", "06:50:00"),
    ]

    results = []

    for project_id, user_name, commit_title, time in events:
        project = next(
            p for p in MOCK_PROJECTS
            if p["id"] == project_id
        )

        results.append({
            "project_id": project["id"],
            "project_name": project["name"],
            "user_name": user_name,
            "avatar_url": None,
            "timestamp": f"{today} {time}",
            "commit_title": commit_title,
        })

    return results
    

def mock_merge_requests() -> List[Dict[str, Any]]:
    merge_requests = [
        (400, "Fix dashboard loading issue", "Alice", "Bob", False),
        (405, "Improve authentication flow", "Bob", "Fatima", False),
        (419, "Update reusable components", "Diana", "Alice", False),
        (420, "Optimize data processing", "Charlie", "Elias", False),
        (425, "Add export functionality", "Elias", None, False),
        (430, "Fix mobile navigation", "Gustav", "Diana", False),
        (435, "Improve notification handling", "Hanna", "Bob", True),
        (440, "Implement role permissions", "Fatima", None, True),
    ]

    def get_user(name):
        if name is None:
            return {}

        user = next(
            u for u in MOCK_USERS
            if u["name"] == name
        )

        return {
            "name": user["name"],
            "username": user["username"],
            "avatar_url": None,
        }

    results = []

    for project_id, title, author, assignee, draft in merge_requests:
        results.append({
            "title": title,
            "project_id": project_id,
            "author": get_user(author),
            "assignee": get_user(assignee),
            "draft": draft,
        })

    return results

    

def _mock_pipelines_for_project(project_id: int) -> List[Dict[str, Any]]:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    pipelines = [
        (400, 9005, "failed", "main", "Bob", "09:10:00"),
        (405, 9004, "running", "develop", "Alice", "09:00:00"),
        (420, 9003, "pending", "main", "Charlie", "08:45:00"),
        (430, 9002, "canceled", "feature/navigation", "Gustav", "08:30:00"),
        (419, 9001, "success", "main", "Diana", "08:15:00"),
    ]

    results = []

    for pid, pipeline_id, status, branch, user_name, time in pipelines:
        project = next(
            p for p in MOCK_PROJECTS
            if p["id"] == pid
        )

        results.append({
            "project_id": project["id"],
            "project_name": project["name"],
            "pipeline_id": pipeline_id,
            "status": status,
            "ref": branch,
            "updated_at": f"{today}T{time}Z",
            "user_name": user_name,
            "avatar_url": None,
            "web_url": None,
        })

    return results



def mock_team_activity() -> List[Dict[str, Any]]:
    today = datetime.now().strftime("%Y-%m-%d")

    active_users = {"Alice", "Bob", "Charlie", "Diana", "Elias", "Fatima", "Gustav", "Hanna"}

    results = []

    for user in MOCK_USERS:
        is_active = user["name"] in active_users

        results.append({
            "name": user["name"],
            "username": user["username"],
            "avatar_url": None,
            "online": is_active,
            "last_activity": today if is_active else "No activity",
        })

    return results
