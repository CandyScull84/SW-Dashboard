# api/pipelines.py

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from .current_projects import iter_group_projects, get_project_name
from .mock_data import _mock_pipelines_for_project
from .gitlab_client import gitlab
from ..config import GITLAB_GROUP_ID, USE_MOCK

VALID_BAD_STATUSES = {"failed", "running", "pending", "canceled"}

# -----------------
# Helpers
# -----------------

def _safe_dt_obj(raw: Optional[str]) -> datetime:
    """ISO8601 - datetime, handle Z and milliseconds"""
    if not raw:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    try:
        clean = raw.replace("Z", "+00:00")
        return datetime.fromisoformat(clean)
    except Exception:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)

def _safe_dt_str(raw: Optional[str]) -> str:  
    dt = _safe_dt_obj(raw)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# -----------------
# Fetch ALL pipelines (pagination allowed)
# -----------------
# def get_all_recent_pipelines(project_id: int, max_pages: int = 5, per_page: int = 20) -> List[Dict[str, Any]]:
#     """
#     Hämtar upp till max_pages pipeline-sidor för att garantera att vi hittar senaste pipeline.
#     """
#     all_pipes = []

#     for page in range(1, max_pages + 1):
#         data, headers = gitlab.get(
#             f"/projects/{project_id}/pipelines",
#             params={
#                 "page": page,
#                 "per_page": per_page,
#                 "order_by": "id",  # viktigast – ID är strikt stigande
#                 "sort": "desc"
#             },
#             include_headers=True,
#         )

#         if not data:
#             break

#         all_pipes.extend(data)

#         next_page = headers.get("X-Next-Page")
#         if not next_page or next_page == "0":
#             break

    # return all_pipes
def get_all_recent_pipelines(project_id: int) -> List[Dict[str, Any]]:
    """
    Gets the latest pipeline (per_page=1).
    """

    data = gitlab.get(
        f"/projects/{project_id}/pipelines",
        params={
            "per_page": 1,
            "order_by": "id",  # viktigast – ID är strikt stigande
            "sort": "desc"
        },
    )

    return data or []

# -----------------
# Get recent failed pipeline
# -----------------

def get_recent_failing_pipelines(
    group_id: int = GITLAB_GROUP_ID,
    limit_projects: int = 1000,
    include_subgroups: bool = True,
    branch: Optional[str] = None,
) -> List[Dict[str, Any]]:
    print("DEBUG: Running get_recent_failing_pipelines() — USE_MOCK =", USE_MOCK)
    results: List[Dict[str, Any]] = []
    checked = 0

    if USE_MOCK:
        return [
            p for p in _mock_pipelines_for_project(9000)
            if p.get("status") in VALID_BAD_STATUSES
        ]

    for proj in iter_group_projects(
        group_id=group_id,
        per_page=100,
        include_subgroups=include_subgroups
    ):
        pid = proj.get("id")
        pname = get_project_name(pid)

        # project_info = gitlab.get_project(pid)
        # is_archived = project_info.get("archived", False)
        
        is_archived = proj.get("archived", False)
        
        if is_archived:
            print(f"Skipping archived project: {pname}")
            continue
        
        try:
            pipelines = get_all_recent_pipelines(pid)
        except Exception as e:
            print(f"⚠️ Failed to load pipelines for {pname}: {e}")
            continue
        
        # DEBUG - Does Gitlab send any pipelines?
        print(f"\n---Pipelines for {pname} (id={pid})---")
        for pp in pipelines[:5]:
            print(f" id={pp.get('id')} status={pp.get('status')} updated={pp.get('updated_at')}")
        
        if not pipelines:
            continue

        # sortera så senaste alltid är pipelines[0]
        pipelines.sort(key=lambda p: _safe_dt_obj(p.get("updated_at")), reverse=True)
        latest = pipelines[0]
        status = latest.get("status")

        # 1 — If success → Skip
        if status == "success":
            continue

        # 2 If status not failed, running, pending, canceled
        if status not in VALID_BAD_STATUSES:
            continue

        # Hämta detaljer (används för avatar etc.)
        details = get_pipeline_details(pid, latest.get("id"))
        username = (details.get("user") or {}).get("username")
        user = gitlab.get_user_by_username(username) or {}

        updated_str = _safe_dt_str(latest.get("updated_at"))

        # Bygg pipeline-objektet
        results.append({
            "project_id": pid,
            "project_name": pname,
            "pipeline_id": latest.get("id"),
            "status": status,
            "ref": latest.get("ref"),
            "updated_at": updated_str,
            "user_name": user.get("name"),
            "avatar_url": user.get("avatar_url"),
            "web_url": latest.get("web_url") or details.get("web_url"),
            "archived": is_archived,
        })

        checked += 1
        if checked >= limit_projects:
            break

    # Sortera slutresultat på datum
    results.sort(key=lambda r: _safe_dt_obj(r["updated_at"]), reverse=True)

    print(f"DEBUG: Returning {len(results)} failing/non-success pipelines")
    return results

# -----------------
# pipeline details
# -----------------

def get_pipeline_details(project_id: int, pipeline_id: int) -> Dict[str, Any]:
    try:
        data = gitlab.get(f"/projects/{project_id}/pipelines/{pipeline_id}")
        return data or {}
    except Exception:
        return {}