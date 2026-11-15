"""TikTok OAuth 2.0 (desktop flow with PKCE) — token storage and refresh."""

import hashlib
import json
import os
import secrets
import time
import urllib.parse
from pathlib import Path

import requests

TOKEN_FILE = Path(".tiktok_tokens.json")

AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
REVOKE_URL = "https://open.tiktokapis.com/v2/oauth/revoke/"

SCOPES = "user.info.basic,video.upload"


def new_code_verifier() -> str:
    return secrets.token_urlsafe(64)


def get_auth_url(client_key: str, redirect_uri: str, code_verifier: str, state: str) -> str:
    # TikTok's desktop flow wants the SHA-256 of the verifier hex-encoded, not base64url.
    params = {
        "client_key": client_key,
        "scope": SCOPES,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "state": state,
        "code_challenge": hashlib.sha256(code_verifier.encode()).hexdigest(),
        "code_challenge_method": "S256",
    }
    return f"{AUTH_URL}?{urllib.parse.urlencode(params)}"


def _token_request(payload: dict) -> dict:
    resp = requests.post(TOKEN_URL, data=payload, timeout=30)
    data = resp.json()
    if "access_token" not in data:
        raise RuntimeError(f"TikTok token request failed: {data.get('error')}: {data.get('error_description')}")
    return data


def exchange_code(client_key: str, client_secret: str, code: str, redirect_uri: str, code_verifier: str) -> dict:
    data = _token_request({
        "client_key": client_key,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
    })
    _save_tokens(data)
    return data


def refresh_access_token(client_key: str, client_secret: str, refresh_token: str) -> dict:
    data = _token_request({
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    })
    _save_tokens(data)
    return data


def load_tokens() -> dict:
    if not TOKEN_FILE.exists():
        raise FileNotFoundError(
            "No TikTok tokens found. Run `python tiktok_auth.py` first, "
            "or set TIKTOK_REFRESH_TOKEN."
        )
    return json.loads(TOKEN_FILE.read_text())


def get_valid_access_token(client_key: str, client_secret: str) -> str:
    """Use the saved token file if present; otherwise start from TIKTOK_REFRESH_TOKEN."""
    if TOKEN_FILE.exists():
        tokens = load_tokens()
        if tokens.get("expires_at", 0) - time.time() >= 300:
            return tokens["access_token"]
        refresh_token = tokens["refresh_token"]
    else:
        refresh_token = os.getenv("TIKTOK_REFRESH_TOKEN")
        if not refresh_token:
            load_tokens()
    return refresh_access_token(client_key, client_secret, refresh_token)["access_token"]


def _save_tokens(data: dict) -> None:
    tokens = {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token", ""),
        "open_id": data.get("open_id", ""),
        "scope": data.get("scope", ""),
        "expires_at": time.time() + data.get("expires_in", 86400),
        "refresh_expires_at": time.time() + data.get("refresh_expires_in", 2592000),
    }
    TOKEN_FILE.write_text(json.dumps(tokens, indent=2))
