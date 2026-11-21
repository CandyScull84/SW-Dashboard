# api/current_projects.py
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Tuple, Optional
from .mock_data import mock_push_events
from .gitlab_client import gitlab
from ..config import GITLAB_GROUP_ID, USE_MOCK

# =========================
# Helpers
# =========================

def _safe_parse_ts(raw: Optional[str]) -> str:
    if not raw:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _ts_to_datetime(item: Dict[str, Any]) -> datetime:
    try:
        return datetime.fromisoformat(item.get("timestamp", ""))
    except Exception:
        return datetime.now()

def _to_int(v: Optional[str]) -> Optional[int]:
    try:
        return int(v) if v and v.strip() else None
    except ValueError:
        return None

# =========================
# Project name (cached)
# =========================

def get_project_name(project_id: int) -> str:
    if not project_id:
        return "Unknown project"
    data = gitlab.get_project(project_id)
    if not data:
        return f"Project #{project_id}"
    return data.get("path_with_namespace") or data.get("name") or f"Project #{project_id}"

# =========================
# Projects (Pagination)
# =========================
def get_group_projects_page(
    group_id: int,
    page: int = 1,
    per_page: int = 100,
    include_subgroups: bool = True,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
   
    params = {
        "page": page,
        "per_page": per_page,
        "include_subgroups": "true" if include_subgroups else "false",
        "order_by": "last_activity_at",
        "sort": "desc",
    }
    
    data, headers = gitlab.get(
        f"/groups/{group_id}/projects",
        params=params,
        include_headers=True,
    ) or ([], {})
    
    if not data:
        return [], {
            "page": page, 
            "per_page": per_page, 
            "next_page": None,
            "prev_page": None,
            "total_pages": None,
            "total_items": None
        }
   
    meta = {
        "page": _to_int(headers.get("X-Page")),
        "per_page": _to_int(headers.get("X-Per-Page")),
        "next_page": _to_int(headers.get("X-Next-Page")),
        "prev_page": _to_int(headers.get("X-Prev-Page")),
        "total_pages": _to_int(headers.get("X-Total-Pages")),
        "total_items": _to_int(headers.get("X-Total")),
    }
    return data, meta

def iter_group_projects(group_id: int, per_page: int = 100, include_subgroups: bool = True):
    """
    Generator that iterates through ALL pages of /groups/:id/projects
    and yields one project at a time (memory-efficient).
    """
    page = 1
    while True:
        items, meta = get_group_projects_page(
            group_id=group_id,
            page=page,
            per_page=per_page,
            include_subgroups=include_subgroups,
        )
        for p in items:
            yield p
        if not meta.get("next_page"):
            break
        page = meta["next_page"]

def find_projects_by_name(group_id: int, name_contains: str, per_page: int = 100, include_subgroups: bool = True) -> List[Dict[str, Any]]:
    """Simple search across all pages (case-insensitive)."""
    needle = (name_contains or "").strip().lower()
    if not needle:
        return []
    matches = []
    for p in iter_group_projects(group_id, per_page, include_subgroups):
        if needle in (p.get("name") or "").lower():
            matches.append(p)
    return matches

def find_project_by_id(group_id: int, project_id: int, per_page: int = 100, include_subgroups: bool = True) -> Optional[Dict[str, Any]]:
    """Find a project by ID by looping through all pages."""
    for p in iter_group_projects(group_id, per_page, include_subgroups):
        if p.get("id") == project_id:
            return p
    return None
    
# =========================
# Commits -> "push events"
# =========================

# def get_project_commits(project_id: int, limit: int = 5) -> List[Dict[str, Any]]:
#     data, _ = gitlab.get(
#         f"/projects/{project_id}/repository/commits",
#         params={"per_page": limit},
#         include_headers=True,
#     )
#     return data or []
    
# def map_commit_to_event(commit: Dict[str, Any], project: Dict[str, Any]) -> Dict[str, Any]:
#     # email = commit.get("author_email", "")
#     return {
#         "project_id": project["id"],
#         "project_name": project.get("name") or get_project_name(project["id"]),
#         "user_name": commit.get("author_name", "unknown-user"),
#         # "avatar_url": get_user_avatar(email),
#         "avatar_url": None,
#         "timestamp": _safe_parse_ts(commit.get("created_at")),
#         "commit_title": commit.get("title", ""),
#     }
    
# =========================
# Push events (senaste commits per projekt)
# =========================

def get_recent_push_events(
    group_id: int = GITLAB_GROUP_ID,
    limit: int = 8,
    include_subgroups: bool = True,
    exclude_archived: bool = True
) -> List[Dict[str, Any]]:
    if USE_MOCK:
        return mock_push_events()[:limit]
    
    print("DEBUG: Loading recent push events…")

    events: List[Dict[str, Any]] = []

    # ---- 1. Hämta projektlistan (redan sorterad: senaste aktivitet först) ----
    projects = gitlab.get(
        f"/groups/{group_id}/projects",
        params={
            "include_subgroups": "true" if include_subgroups else "false",
            "order_by": "last_activity_at",
            "sort": "desc",
            "archived": "false" if exclude_archived else "null",
            "per_page": 100,
        },
        include_headers=True,
    )[0]

    if not isinstance(projects, list):
        return []

    # ---- 2. Gå igenom projekt i ordning och hämta bara TILLS vi hittat limit pushes ----
    for p in projects:  # inga slice — vi slutar själva
        pid = p.get("id")
        if not pid:
            continue

        # ---- 3. Hämta senaste commit (cache finns i gitlab-client) ----
        commits = gitlab.get_latest_commit(pid)
        if not commits:
            continue

        c = commits[0]  # kortare variabelnamn
        email = c.get("author_email")
        user = gitlab.get_user_by_email(email) if email else None
        avatar_url = user.get("avatar_url") if user else None
        
        # Build push event
        events.append({
            "project_id": pid,
            "project_name": p.get("name") or "(unknown)",
            "project_fullpath": p.get("path_with_namespace"),
            "web_url": p.get("web_url"),
            "user_name": c.get("author_name", "(unknown)"),
            "user_id": user.get("id") if user else None,
            "avatar_url": avatar_url,  
            "timestamp": _safe_parse_ts(c.get("created_at")),
            "commit_title": c.get("title", ""),
        })

        # ---- 5. Stoppa när limit är nådd ----
        if len(events) >= limit:
            break

    # ---- 6. Sortera pushar i rätt ordning ----
    events.sort(key=lambda e: e["timestamp"], reverse=True)

    return events[:limit]


def get_active_project_summary(
    group_id: int = GITLAB_GROUP_ID,
    days: int = 1,
    include_subgroups: bool = True,
    exclude_archived: bool = True
) -> Dict[str, Any]:
    """
    Summerar hur många projekt som varit aktiva de senaste 'days' dagarna.
    Återanvänder befintliga projektfunktioner.
    """
    if USE_MOCK:
        events = mock_push_events()

        active_projects = [
            {
                "project_id": event["project_id"],
                "project_name": event["project_name"],
                "name_with_namespace": event["project_name"],
                "path_with_namespace": event["project_name"],
                "web_url": None,
                "last_activity": event["timestamp"][:10],
            }
            for event in events
        ]

        return {
            "total_projects": len(active_projects),
            "active_projects": len(active_projects),
            "inactive_projects": 0,
            "active_ratio": 1.0,
            "active_list": active_projects,
        }

    today = datetime.now(timezone.utc).date()
    cutoff = today - timedelta(days=days)

    # 🟦 Hämta alla projekt via befintlig generator
    projects = list(iter_group_projects(group_id, per_page=100, include_subgroups=include_subgroups))

    active_projects = []
    inactive_projects = []

    for p in projects:
        if exclude_archived and p.get("archived"):
            continue

        ts = p.get("last_activity_at")
        if not ts:
            inactive_projects.append(p)
            continue

        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)
            if dt.date() >= cutoff:
                active_projects.append({
                    "project_id": p.get("id"),
                    "project_name": p.get("name"),
                    "name_with_namespace": p.get("name_with_namespace"),
                    "path_with_namespace": p.get("path_with_namespace"),
                    "web_url": p.get("web_url"),
                    "last_activity": dt.strftime("%Y-%m-%d"),
                })
            else:
                inactive_projects.append(p)
        except Exception:
            inactive_projects.append(p)

    summary = {
        "total_projects": len(projects),
        "active_projects": len(active_projects),
        "inactive_projects": len(inactive_projects),
        "active_ratio": round(len(active_projects) / len(projects), 2) if projects else 0.0,
        "active_list": active_projects,
    }

    print(f"📊 Aktiva projekt: {summary['active_projects']} av {summary['total_projects']}")
    return summary


