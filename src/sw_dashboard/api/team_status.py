import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from typing import List, Dict, Any
from .gitlab_client import gitlab
from .current_projects import iter_group_projects
from .current_projects import get_recent_push_events
from .merge_requests import show_active_merge_requests
from .pipelines import get_recent_failing_pipelines
from .mock_data import mock_team_activity
from ..config import GITLAB_GROUP_ID, GITLAB_MEMBER_GROUP_ID, USE_MOCK

load_dotenv()

def _safe_dt(raw: str) -> datetime | None:
    """Try  ISO8601-date from GitLab."""
    if not raw:
        return None
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def get_team_activity(member_group_id: int = GITLAB_MEMBER_GROUP_ID, project_group_id: int = GITLAB_GROUP_ID) -> List[Dict[str, Any]]:
    if USE_MOCK:
        return mock_team_activity()
    
    IGNORE_USERS = [u.strip() for u in os.getenv("IGNORE_USERS", "").split(",") if u.strip()]
    """Returning a list over team members and if they had activity today."""
    members, _ = gitlab.get(f"/groups/{member_group_id}/members/all", include_headers=True)
    if not isinstance(members, list):
        print("⚠️ Ingen giltig medlemsdata från GitLab:", members)
        return []

    now = datetime.now(timezone.utc)
    today = now.date()
    # cutoff = now - timedelta(days=1)

    # Hämta projektaktivitet
    projects = list(iter_group_projects(group_id=project_group_id, per_page=100))
    print(f"DEBUG: Hämtade {len(projects)} projekt för aktivitetskontroll.")

    # Hämta events (frivilligt, som tidigare)
    try:
        pushes = get_recent_push_events(limit=50, group_id=project_group_id) or []
        merge_reqs = show_active_merge_requests(group_id=project_group_id) or []
        pipelines = get_recent_failing_pipelines(group_id=project_group_id) or []
    except Exception as e:
        print(f"⚠️ Fel vid hämtning av eventdata: {e}")
        pushes, merge_reqs, pipelines = [], [], []

    results = []

    for m in members:
        user = m.get("user", m)
        username = user.get("username") or m.get("user_name")
        name = user.get("name") or m.get("name")
        avatar_url = user.get("avatar_url") or m.get("avatar_url")
        
        if username in IGNORE_USERS:
            print(f"⏩ Ignorerar användare: {username}")
            continue

        # Starta som offline
        online = False
        last_activity = None

        # 🔹 1. Projektaktivitet
        for pr in projects:
            dt = _safe_dt(pr.get("last_activity_at"))
            if not dt:
                continue
            if not pr.get("last_activity_at"):
                continue
            if dt and dt.date() == today:
                online = True
                last_activity = dt
                break

        # 🔹 2. Push / MR / Pipeline (kompletterande)
        if not online:
            for p in pushes:
                if p.get("user_name") == username:
                    dt = _safe_dt(p.get("timestamp"))
                    if dt and dt.date() == today:
                        online = True
                        last_activity = dt
                        break

        if not online:
            for mr in merge_reqs:
                author = mr.get("author") or {}
                if author.get("username") == username:
                    dt = _safe_dt(mr.get("updated_at") or mr.get("created_at"))
                    if not dt:
                        continue
                    if not (mr.get("updated_at") or mr.get("created_at")):
                        continue
                    if dt and dt.date() == today:
                        online = True
                        last_activity = dt
                        break

        if not online:
            for pl in pipelines:
                if pl.get("user_name") == username:
                    dt = _safe_dt(pl.get("updated_at"))
                    if not dt:
                        continue
                    if not pl.get("updated_at"):
                        continue
                    if dt and dt.date() == today:
                        online = True
                        last_activity = dt
                        break

        results.append({
            "name": name,
            "username": username,
            "avatar_url": avatar_url,
            "online": online,
            "last_activity": last_activity.strftime("%Y-%m-%d") if last_activity else "No activity",
        })

    # results.sort(key=lambda r: (not r["online"], r["name"].lower()))
    print(f"✅ {sum(1 for r in results if r['online'])} av {len(results)} medlemmar är online idag.")
    return results

