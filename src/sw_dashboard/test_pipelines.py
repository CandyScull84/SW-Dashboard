from api.pipelines import get_all_recent_pipelines, get_recent_failing_pipelines
from api.current_projects import iter_group_projects
from config import GITLAB_API_URL, GITLAB_TOKEN, GITLAB_GROUP_ID
# import urllib3

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("\n=== TEST: Pipelines ===")
print(f"Using GitLab API: {GITLAB_API_URL}")
print(f"Token present: {'yes' if bool(GITLAB_TOKEN) else 'no'}")

# 🧩 1. Testa att GitLab API svarar
try:
    from api.gitlab_client import gitlab
    data, headers = gitlab.get("/projects", include_headers=True)
    if data is None:
        raise RuntimeError("GitLab API returned no data")

    print(f"✅ API OK - {len(data)} projects found")
except Exception as e:
    print(f"❌ GitLab API connection failed: {e}")
    exit()

# 🧩 2. Hämta projekt i gruppen
GROUP_ID = GITLAB_GROUP_ID
print(f"\n→ Listing projects in group {GROUP_ID}:")
projects = list(iter_group_projects(group_id=GROUP_ID))
if not projects:
    print("⚠️ No projects found for this group_id.")
    exit()
print(f"✅ Found {len(projects)} projects.")

# 🧩 3. Visa pipelines för flera projekt
print("\n→ Showing recent pipelines for first 5 projects:")
for project in projects[:5]:
    pid = project["id"]
    pname = project["name"]
    print(f"\n🔹 Project: {pname} (id={pid})")
    try:
        pipelines = get_all_recent_pipelines(pid)
        if not pipelines:
            print("⚠️ No pipelines found.")
        else:
            for p in pipelines:
                print(f" • {p['status']} | {p['ref']} | {p['updated_at']}")
    except Exception as e:
        print(f"❌ Error fetching pipelines: {e}")

# 🧩 4. Hämta failade pipelines i hela gruppen
print("\n→ Fetching recent failing pipelines in group:")
failing = get_recent_failing_pipelines(group_id=GROUP_ID, limit_projects=10)
print(f"✅ Found {len(failing)} failing pipelines.")
for p in failing:
    print(f" • {p['project_name']} | {p['status']} | {p['ref']} | {p['updated_at']}")
