"""
Google OAuth2 authentication handler.
Handles Gmail + Calendar scopes via a single OAuth flow.
Stores tokens in token.json, prompts for re-auth when expired.
"""

import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from config.settings import GOOGLE_SCOPES
from utils.logger import get_logger

log = get_logger("google_auth")

TOKEN_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "token.json")
CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials.json")


def get_google_credentials() -> Credentials:
    """
    Return valid Google OAuth2 credentials.
    - Loads from token.json if available and valid.
    - Refreshes if expired.
    - Runs full OAuth flow if no token exists.
    """
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, GOOGLE_SCOPES)
        log.info("Loaded existing token from %s", TOKEN_PATH)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        log.info("Token expired, refreshing...")
        try:
            creds.refresh(Request())
            _save_token(creds)
            return creds
        except Exception as e:
            log.warning("Token refresh failed: %s — re-authenticating", e)

    # Full OAuth flow
    if not os.path.exists(CREDENTIALS_PATH):
        log.error(
            "credentials.json not found at %s. "
            "Download it from Google Cloud Console → APIs & Services → Credentials → "
            "OAuth 2.0 Client IDs → Download JSON.",
            CREDENTIALS_PATH,
        )
        sys.exit(1)

    log.info("Starting OAuth2 flow — a browser window will open...")
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, GOOGLE_SCOPES)
    creds = flow.run_local_server(port=0)
    _save_token(creds)
    log.info("OAuth2 authentication successful.")
    return creds


def _save_token(creds: Credentials):
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())
    log.info("Token saved to %s", TOKEN_PATH)
