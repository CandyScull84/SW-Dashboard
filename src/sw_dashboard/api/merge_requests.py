# import requests
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta, timezone
from .gitlab_client import gitlab
from .mock_data import mock_merge_requests
from .current_projects import get_project_name
from ..config import GITLAB_GROUP_ID, USE_MOCK

# ==================
# Helpers
# ==================
def _safe_dt(raw:Optional[str]) -> Optional[datetime]:
    """convert datetimeobject (UTC)"""
    if not raw:
        return datetime(1970, 1, 1)
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return datetime(1970, 1, 1)
    
def _to_int(v: Optional[str]) -> Optional[int]:
    try:
        return int(v) if v and v.strip() else None
    except ValueError:
        return None
    
def _is_draft(mr: Dict[str, Any]) -> bool:
    title = (mr.get("title") or "").strip().lower()
    return bool (
        mr.get("work_in_progress")
        or mr.get("draft")
        or title.startswith("wip")
        or title.startswith("draft:")
        or title.startswith("draft -")
    )
        
# ==================
# Pagination
# ==================

def get_group_merge_requests_page(
    group_id:int = GITLAB_GROUP_ID,
    page:int = 1,
    per_page:int = 50,
    state:str = "opened",
    include_drafts: bool = False,
) -> Tuple[List[Dict[str,Any]], Dict[str, Any]]:
 
    if USE_MOCK:
        items = mock_merge_requests()
        if state != "all":
            #Mocken saknar state - vi låtsas att allt är 'opened'
            items = items
        if not include_drafts:
            items = [m for m in items if not _is_draft(m)]
        total = len(items)
        start = (page - 1) * per_page 
        end = start + per_page
        sliced = items[start:end]
        meta = {
            "page": page,
            "per_page": per_page,
            "next_page": page + 1 if end < total else None,
            "prev_page": page - 1 if page > 1 else None,
            "total_pages": (total + per_page - 1) // per_page if per_page else 1,
            "total_items": total,
        }
        return sliced, meta
    # Real API-request
    params = {
        "scope": "all",
        "state": state,
        "order_by":  "updated_at",
        "sort": "desc",
        "per_page": per_page,
        "page": page,
    }
    # url = f"{GITLAB_API_URL}/groups/{group_id}/merge_requests"
    # headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    # params = {
    #     "scope": "all",  # Only fetch open merge requests
    #     "state": state,  # Exclude work-in-progress or draft MRs
    #     "order_by": "updated_at",
    #     "sort": "desc",
    #     "per_page": per_page,
    #     "page": page,
    # }

    # resp = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
    # resp.raise_for_status()
    # items = resp.json() if isinstance(resp.json(), list) else resp.json().get("items", [])
    data, headers = gitlab.get(f"/groups/{group_id}/merge_requests", params=params, include_headers=True,)
    if not data:
        return [], {
            "page": page, 
            "per_page": per_page, 
            "next_page": None,
            "prev_page": None,
            "total_pages": None,
            "total_items": None
            }
    
    if not include_drafts:
        data = [m for m in data if not _is_draft(m)]
        
    meta = {
        "page": _to_int(headers.get("X-Page")),
        "per_page": _to_int(headers.get("X-Per-Page")),
        "next_page": _to_int(headers.get("X-Next-Page")),
        "prev_page": _to_int(headers.get("X-Prev-Page")),
        "total_pages": _to_int(headers.get("X-Total-Pages")),
        "total_items": _to_int(headers.get("X-Total")),
    }
    return data, meta

# ==================
# Terminal, fetch all pages
# ==================

def show_active_merge_requests(group_id: int = GITLAB_GROUP_ID, debug: bool = False) -> List[Dict[str, Any]]:
    # Return mock data if mock mode is enabled
    if USE_MOCK:
        return[m for m in mock_merge_requests() if not _is_draft(m)]
        # return mock_merge_requests()

    # Construct GitLab API request
    # url = f"{GITLAB_API_URL}/groups/{group_id}/merge_requests"
    # headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    # params = {
    #     "scope": "all",
    #     "state": "opened",  # Only fetch open merge requests
    #     "order_by": "updated_at",
    #     "sort": "desc",
    #     "per_page": 100,
    #     "page": 1,
    # }
    
    result: List[Dict[str, Any]] = []
    page = 1
    
    today = datetime.now(timezone.utc)
    earliest_date = today - timedelta(days=3) if today.weekday() == 0 else today - timedelta(days=1)
    
    while True:
        data, meta = get_group_merge_requests_page(
            group_id=group_id,
            page=page,
            per_page=100,
            state="opened",
            include_drafts=False,
        )
        # try:
        #     # Send GET request to GitLab API
        #     resp = requests.get(url, params=params, headers=headers, timeout=10, verify=False)
        #     resp.raise_for_status()
        # except requests.exceptions.RequestException as err:
        #     print(f"❌ API request failed on page {params['page']}: {err}")
        #     break
        
        # data = resp.json()
        if not data:
            print("No open merge requests (excluding WIP/draft-status).")
            break

        
        for mr in data:
            if _is_draft(mr) or mr.get("state") != "opened":
                continue
            
            created_at = _safe_dt(mr.get("created_at"))
            if not created_at or created_at < earliest_date:
                continue

            
            # Extract relevant fields from each merge request
            title = mr.get("title")
            project_id = mr.get("project_id")
            author = mr.get("author", {})
            assignee = mr.get("assignee", {})

            if debug:
                print(f"\n ◆ Title: {title}")
                print(f"   Project ID: {project_id}")
                print(f"   Author: {author.get('name')} ({author.get('username')})")
                print(f"   Author Avatar: {author.get('avatar_url')}")
                if assignee:
                    print(f"   Assignee: {assignee.get('name')} ({assignee.get('username')})")
                    print(f"   Assignee Avatar: {assignee.get('avatar_url')}")
                else:
                    print("   Assignee: None")

            # Add structured data to result list
            result.append(
                {
                    "title": mr.get("title"),
                    "description": mr.get("description"),
                    "created_at": mr.get("created_at"),
                    "project_id": project_id,
                    "project_name": get_project_name(project_id),
                    "references": mr.get("references", {}).get("full"),
                    "web_url": mr.get("web_url"),
                    "author": {
                        "name": author.get("name"),
                        "username": author.get("username"),
                        "avatar_url": author.get("avatar_url"),    
                    },
                    "assignee": {
                        "name": assignee.get("name"),
                        "username": assignee.get("username"),
                        "avatar_url": assignee.get("avatar_url"), 
                    } if assignee else None,
                })
        
        if not meta.get("next_page"):
            break
        page = meta["next_page"]
    
    result.sort(key=lambda m: m["created_at"], reverse=True)
    
        # next_page = headers.get("X-Next-Page")
        # if not next_page:
        #     break
        # params["page"] = int(next_page)
            
    if debug:
        print(f"\n✅ Total merge requests fetched: {len(result)}")
    
    return result
        
    

# -------------------
# Dashboard summary
# -------------------

def get_merge_requests_per_person(group_id: int = GITLAB_GROUP_ID) -> List[Dict[str, Any]]:
    data = show_active_merge_requests(group_id=group_id, debug=False)
    if not isinstance(data, list):
        return []

    result = []
    for mr in data:
        # Extract and simplify relevant fields
        author = mr.get("author") or {}
        assignee = mr.get("assignee") or {}
        project_id = mr.get("project_id")


        result.append(
            {
                "author_name": author.get("name"),
                "assignee_name": assignee.get("name"),
                "title": mr.get("title"),
                "description": mr.get("description"),
                "project_id": project_id,
                "project_name": get_project_name(project_id),
                "references": mr.get("references", {}).get("full"),
                "waiting_for_review": bool(assignee.get("name")),
            }
        )

    return result



