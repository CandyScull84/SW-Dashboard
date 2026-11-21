# Import functions that retrieve merge request data
from api.merge_requests import show_active_merge_requests, get_merge_requests_per_person
from api.current_projects import get_recent_push_events, get_recent_active_projects_fast, get_latest_project_pushes
from api.pipelines import get_recent_failing_pipelines
from config import GITLAB_GROUP_ID
from api.current_projects import get_project_name
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Entry point for the terminal-based dashboard
def main():
    while True:
        # Display the main menu
        print("\n=== SW Dashboard ===")
        print("1. Show all open merge requests (excluding WIP/draft)")
        print("2. Show dashboard view (who is waiting / responsible)")
        print("3. Show recent project pushes")
        print("4. Show recent active projects")
        print("5. Show latest project pushes")
        print("6. Show recent failing pipelines")
        print("0. Exit")

        # Get user input
        val = input("Choose an option: ")

        # Option 1: Show all open merge requests
        if val == "1":
            merge_requests = show_active_merge_requests()
            if not merge_requests:
                print("No open merge requests.")
            else:
                print("\nOpen merge requests:")
                for mr in merge_requests:
                    project_id = mr["project_id"]
                    project_display = mr.get("project_name") or get_project_name(project_id)
                    
                    # Display basic information about each merge request
                    print(f"\n ◆ Title: {mr['title']}")
                    print(f"   Project: {project_display} (id{project_id})")
                    print(
                        f"   Author: {mr['author']['name']} ({mr['author']['username']})"
                    )
                    # Check if an assignee exists and display accordingly
                    if mr["assignee"] and mr["assignee"].get("name"):
                        print(
                            f"   Assignee: {mr['assignee']['name']} ({mr['assignee']['username']})"
                        )
                    else:
                        print("   Assignee: None")
        # Option 2: Show dashboard view (who is waiting for review)
        elif val == "2":
            dashboard_view()
        # Option 3: Show recent push events
        elif val == "3":
            events = get_recent_push_events(limit=5)
            if not events:
                print("No recent pushes found.")
            else:
                print("\nRecent project pushes:")
                for e in events:
                    print(
                        f" • Project: {e['project_name']} ({e['project_id']}) | "
                        f"User: {e['user_name']} | Avatar: {e['avatar_url']} | "
                        f"Time: {e['timestamp']} | Commit: {e['commit_title']}"
                    )
        # option 4: show recent active projects
        elif val == "4":
            items = get_recent_active_projects_fast(group_id=GITLAB_GROUP_ID, limit=5)
            print("\nRecent active projects(FAST):")
            for e in items:
                print(f" • {e['project_name']} - {e['user_name']} ({e['timestamp']})")
                
        # option 5: show latest project pushes
        elif val == "5":
            items = get_latest_project_pushes(group_id=GITLAB_GROUP_ID, limit=5)
            print("\nLatest project pushes(FAST):")
            for e in items:
                print(f" • {e['project_name']} - {e['user_name']} ({e['timestamp']})" + (f" | {e['commit_title']}" if e.get('commit_title') else ""))
        
        elif val == "6":
            items = get_recent_failing_pipelines(group_id=GITLAB_GROUP_ID, limit_projects=20, include_subgroups=True, only_official_path_prefix="projects/", branch=None
            )
            if not items:
                print("\nNo failing pipelines found.")
            else:
                print("\nRecent failing pipelines:")
                for x in items:
                    print(
                        f" • {x['project_name']} - {x.get('user_name') or 'unknown'}"
                        f"({x['updated_at']}) | {x['status']} | {x.get('ref') or ''}"
                        f" | {x.get('web_url') or ''}"
                    )
        # Option 0: Exit the program
        elif val == "0":
            print("Exiting...")
            break
        # Invalid input
        else:
            print("Invalid choice, please try again.")


# Displays a simplified dashboard view showing review responsibilities
def dashboard_view():
    merge_requests = get_merge_requests_per_person()

    if not merge_requests:
        print(" No open merge requests at the moment.")
        return
    else:
        print("\nOpen merge requests:")
        for mr in merge_requests:
            print(f"\n ◆ Title: {mr['title']}")
            print(f"   Project ID: {mr['project_id']}")
            print(f"   Author: {mr['author_name']}")

            # Show whether the merge request is waiting for review or unassigned
            if mr["waiting_for_review"]:
                print(
                    f"🔔 {mr['author_name']} is waiting for {mr['assignee_name']} to review: {mr['title']}"
                )
            else:
                print(
                    f"📌 {mr['author_name']} has created a merge request with no reviewer assigned: {mr['title']}"
                )

    """
    Old terminal-based dashboard below.
    Kept for reference only.
    Not used by FastAPI or Docker
    """

# Run the main function when the script is executed directly
# if __name__ == "__main__":
#     main()
