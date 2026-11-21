
# config.py

import os
from dotenv import load_dotenv

load_dotenv()

# Demo mode
USE_MOCK = os.getenv("USE_MOCK", "true").lower() == "true"

# GitLab configuration
GITLAB_TOKEN = os.getenv("ACCESS_TOKEN")
GITLAB_API_URL = os.getenv("GITLAB_API_URL", "https://gitlab.com/api/v4")
GITLAB_GROUP_ID = int(os.getenv("GITLAB_GROUP_ID", "0"))
GITLAB_MEMBER_GROUP_ID = int(os.getenv("GITLAB_MEMBER_GROUP_ID", "0"))
