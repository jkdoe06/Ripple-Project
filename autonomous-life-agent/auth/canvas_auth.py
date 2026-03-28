"""
Canvas LMS authentication handler.
Uses a personal access token from Canvas settings.
"""

import sys
import requests
from config.settings import CANVAS_API_URL, CANVAS_API_TOKEN
from utils.logger import get_logger

log = get_logger("canvas_auth")


def get_canvas_session() -> requests.Session:
    """
    Return a requests.Session pre-configured with Canvas API auth headers.
    Validates the token by hitting /api/v1/users/self.
    """
    token = CANVAS_API_TOKEN
    if not token or token == "your_canvas_api_token_here":
        log.error(
            "Canvas API token not set. Get yours from: "
            "bcourses.berkeley.edu → Account → Settings → "
            "New Access Token. Then set CANVAS_API_TOKEN in .env"
        )
        sys.exit(1)

    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    session.base_url = CANVAS_API_URL

    # Validate token
    log.info("Validating Canvas API token...")
    try:
        resp = session.get(f"{CANVAS_API_URL}/users/self")
        resp.raise_for_status()
        user = resp.json()
        log.info("Authenticated as: %s (%s)", user.get("name"), user.get("login_id"))
    except requests.HTTPError as e:
        log.error("Canvas authentication failed: %s", e)
        sys.exit(1)

    return session
