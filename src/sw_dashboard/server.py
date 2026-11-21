# server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import time

from .api.merge_requests import get_group_merge_requests_page
from .api.current_projects import get_recent_push_events, get_active_project_summary
from .api.pipelines import get_recent_failing_pipelines
from .api.team_status import get_team_activity
from .config import GITLAB_GROUP_ID, GITLAB_MEMBER_GROUP_ID

app = FastAPI(title="SW Dashboard API")

# ====================
# CORS ( only needed in dev not in docker.)
# ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ====================
# Simple in-memory-cache
# ====================

CACHE_TTL_SECONDS = 60
_cache = {}

def get_from_cache(key:str):
    """
    Get from cache if there is any and not to old
    """
    entry = _cache.get(key)
    if not entry:
        return None
    
    now = time.time()
    age = now - entry["timestamp"]
    if age > CACHE_TTL_SECONDS:
        #to old ->throw
        _cache.pop(key, None)
        return None
    
    return entry["value"]

def save_to_cache(key: str, value):
    """
    Save value in cache with timestamp
    """
    
    _cache[key] = {
        "value": value,
        "timestamp": time.time(),
    }

# ====================
# FRONTEND STATIC FILES (React/Vite build)
# ====================

IS_DEV = os.getenv("DEV", "1") == "1"
if not IS_DEV:
    from fastapi.staticfiles import StaticFiles
    from pathlib import Path
    
    #Find path to projectRoot
    BASE_DIR = Path(__file__).resolve().parent.parent
    #Static in projectRoot
    STATIC_DIR = BASE_DIR / "static"

    # React build placed in ./static
    if STATIC_DIR.exists():
        app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
    else:
        print(f" Static folder not found: {STATIC_DIR} -running backend only")
    
# Fallback for SPA routing to work
if not IS_DEV:
    @app.get("/{full_path:path}")
    async def spa_fallback(full_path:str):
        index_file = STATIC_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "Frontend not build yet."}

# ====================
# API ROUTES
# ====================

@app.get("/merge-requests")
def list_merge_requests(group_id: int = GITLAB_GROUP_ID, page: int = 1, per_page: int = 20):
    items, meta = get_group_merge_requests_page(
        group_id=group_id,
        page=page,
        per_page=per_page
    )
    return {"items": items, "meta": meta}

@app.get("/push-events")
def list_push_events(group_id: int = GITLAB_GROUP_ID, limit: int = 10):
    items = get_recent_push_events(limit=limit, group_id=group_id)
    return {"items": items}

@app.get("/failing-pipelines")
def list_failing_pipelines(group_id: int = GITLAB_GROUP_ID, limit_projects: int = 10):
    """
    Returning failing pipelines.
    Now with simple cache: same answer reuse in 60 seconds.
    """
    cache_key = f"failing:{group_id}:{limit_projects}"

    # 1. Try get from cache
    cached = get_from_cache(cache_key)
    if cached is not None:
        print(" /failing-pipelines – answer from CACHE")
        return {"items": cached}

    # 2. If nothing in cache → get "for real"
    print(" /failing-pipelines – gets from GitLab (no cache)")
    items = get_recent_failing_pipelines(
        group_id=group_id,
        limit_projects=limit_projects
    )

    # 3. Save in cache
    if items:
        save_to_cache(cache_key, items)

    print(f"===DEBUG: get_recent_failing_pipelines returnerade {len(items)} objekt ===")
    for i, p in enumerate(items[:3]):
        print(f" {i+1}. {p.get('status')} || {p.get('ref')} || {p.get('updated_at')}")

    return {"items": items}

# @app.get("/failing-pipelines")
# def list_failing_pipelines(group_id: int = GITLAB_GROUP_ID, limit_projects: int = 10):
#     print("===DEBUG: Kör /failing-pipelines ===")
#     items = get_recent_failing_pipelines(group_id=group_id, limit_projects=limit_projects)
#     print(f"===DEBUG: get_recent_failing_pipelines returnerade {len(items)} objekt ===")
#     for i, p in enumerate(items[:3]):
#         print(f" {i+1}. {p.get('status')} || {p.get('ref')} || {p.get('updated_at')}")
#     return {"items": items}

@app.get("/team-status")
def team_status(group_id: int = GITLAB_MEMBER_GROUP_ID, project_group_id: int = GITLAB_GROUP_ID):
    items = get_team_activity(member_group_id=group_id, project_group_id=project_group_id)
    print(f"Team-status returnerar {len(items)} medlemmar till klienten")
    return {"items": items}

@app.get("/active-projects")
def list_active_projects(group_id: int = GITLAB_GROUP_ID, days: int = 1):
    """
    Returnerar en summering av aktiva projekt senaste X dagarna.
    """
    summary = get_active_project_summary(group_id=group_id, days=days)
    return {"items": summary}


