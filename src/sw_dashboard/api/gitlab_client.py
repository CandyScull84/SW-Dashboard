import requests
import time
import httpx
from typing import Any, Dict, Optional
from ..config import GITLAB_API_URL, GITLAB_TOKEN

# ====================
# simple cache
# ====================

class SimpleCache:
    """Simple in-memory cache with timelimit (default 10 min)"""
    def __init__(self, ttl_seconds: int = 600):
        self.ttl = ttl_seconds
        self._data: Dict[str, Dict[str, Any]] = {}
        
    def get(self, key: str) -> Optional[Any]:
        entry = self._data.get(key)
        if not entry:
            return None
        if time.time() - entry["timestamp"] > self.ttl:
            # clear old
            self._data.pop(key, None)
            return None
        return entry["value"]
    
    def set(self, key: str, value: Any):
        """save new value in cache"""
        self._data[key] = {"value": value, "timestamp": time.time()}
    
    def clear(self):
        self._data.clear()   
        
# ====================
# Gitlab client
# ====================

class GitLabClient:
    """Shared client for all API-requests to GitLab"""
    def __init__(self, base_url: str = GITLAB_API_URL, token: str = GITLAB_TOKEN):
        self.base_url = base_url.rstrip("/")
        self.headers = {"PRIVATE-TOKEN": token}
        self.timeout = 10
        self.projects = SimpleCache()
        self.users = SimpleCache()
        
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, include_headers: bool = False, with_meta: bool = False,):
        
        """GET-request to GitLab with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            resp = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data  = resp.json()
            if include_headers:
                return data, resp.headers
            return data
        
        except requests.exceptions.RequestException as err:
            print(f" GitLab API error: {err} ({endpoint})")
            
            return (None, {}) if include_headers else None
    
    # ------------------
    # Async version
    # ------------------
    async def aget(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
                   include_headers: bool = False):
        """
        Asynchronous GET using httpx
        """    
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(
                    url, headers=self.headers, params=params
                )
                resp.raise_for_status()
                data=resp.json()
                
                if include_headers:
                    return data, resp.headers
                return data
            except httpx.RequestError as err:
                print(f" GitLab ASYNC API error: {err} ({endpoint})")
                return (None, {}) if include_headers else None
    # ------------------------
    # Helpfunctions with cache
    # ------------------------
    
    def get_project(self, project_id: int):
        """Get info about a project with cache"""
        if not project_id:
            return None
        cache_key = str(project_id)
        cached = self.projects.get(cache_key)
        if cached:
            return cached
        
        data = self.get(f"/projects/{project_id}")
        if data:
            self.projects.set(cache_key, data)
            return data
    
    def get_user_by_email(self, email: str):
        """Get user through email (cache)"""
        if not email:
            return None
        cache_key = email.lower()
        cached = self.users.get(cache_key)
        if cached:
            return cached
        
        data = self.get("/users", params={"search": email})
        if isinstance(data, list) and data:
            user = data[0]
            self.users.set(cache_key, user)
            return user
        return None

    def get_user_by_username(self, username: str):
        """Get user by username (cache)"""
        if not username:
            return None
        cache_key = f"username:{username.lower()}"
        cached = self.users.get(cache_key)
        if cached:
            return cached
        
        data = self.get("/users", params={"username": username})
        if isinstance(data, list) and data:
            user = data[0]
            self.users.set(cache_key, user)
            return user
        return None
    
    def get_user_avatar(self, user_id: int):
        """Get userAvatar by userid (cache)"""
        if not user_id:
            return None
        cache_key = f"avatar:{user_id}"
        cached = self.users.get(cache_key)
        if cached:
            return cached
        
        data = self.get(f"/users/{user_id}")
        if data and isinstance(data, dict):
            avatar = data.get("avatar_url")
            self.users.set(cache_key, avatar)
            return avatar
        
        return None
    
    def get_latest_commit(self, project_id: int):
        """
        Get latest commit for a project
        """
        if not project_id:
            return None
        
        cache_key = f"latest_commit:{project_id}"
        cached = self.projects.get(cache_key)
        if cached:
            return cached
        data = self.get(
            f"/projects/{project_id}/repository/commits",
            params={"per_page":1},
        )
        
        if isinstance(data, list) and data:
            self.projects.set(cache_key, data)
            return data
        return None
    
    
    def iter_group_projects(self, group_id: int, per_page: int = 100, include_subgroups: bool = True):
        """
        Generator that iterates through ALL pages of /groups/:id/projects
        and yields one project at a time (memory-efficient).
        """
        page = 1
        while True:
            params = {
                "page": page,
                "per_page": per_page,
                "include_subgroups": "true" if  include_subgroups else "false",
                "order_by": "last_activity_at",
                "sort": "desc",
            }
            data, headers = self.get(f"/groups/{group_id}/projects", params=params, include_headers=True)
            if not data:
                break
            for p in data:
                yield p
            
            next_page = headers.get("X-Next-Page")
            if not next_page:
                break
            try:
                page = int(next_page)
            except ValueError:
                break
# Create global instance for import
gitlab = GitLabClient()