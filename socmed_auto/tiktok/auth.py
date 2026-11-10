"""TikTok OAuth 2.0 — token storage and refresh."""

import json
import os
import time
from pathlib import Path

import requests

TOKEN_FILE = Path(".tiktok_tokens.json")

AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
REVOKE_URL = "https://open.tiktokapis.com/v2/oauth/revoke/"

SCOPES = "video.publish,video.upload,user.info.basic"


def get_auth_url(client_key: str, redirect_uri: str, state: str = "tiktok_auth") -> str:
    params = (
        f"client_key={client_key}"
        f"&scope={SCOPES}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
    )
    return f"{AUTH_URL}?{params}"


def exchange_code(client_key: str, client_secret: str, code: str, redirect_uri: str) -> dict:
    resp = requests.post(TOKEN_URL, data={
        "client_key": client_key,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    })
    resp.raise_for_status()
    data = resp.json()
    _save_tokens(data)
    return data


def refresh_access_token(client_key: str, client_secret: str) -> dict:
    tokens = load_tokens()
    resp = requests.post(TOKEN_URL, data={
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
    })
    resp.raise_for_status()
    data = resp.json()
    _save_tokens(data)
    return data


def load_tokens() -> dict:
    if not TOKEN_FILE.exists():
        raise FileNotFoundError(
            "No TikTok tokens found. Run `python tiktok_auth.py` first."
        )
    return json.loads(TOKEN_FILE.read_text())


def get_valid_access_token(client_key: str, client_secret: str) -> str:
    tokens = load_tokens()
    # Refresh if expires within 5 minutes
    if tokens.get("expires_at", 0) - time.time() < 300:
        tokens = refresh_access_token(client_key, client_secret)
    return tokens["access_token"]


def _save_tokens(data: dict) -> None:
    tokens = {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token", ""),
        "open_id": data.get("open_id", ""),
        "expires_at": time.time() + data.get("expires_in", 86400),
        "refresh_expires_at": time.time() + data.get("refresh_expires_in", 2592000),
    }
    TOKEN_FILE.write_text(json.dumps(tokens, indent=2))
