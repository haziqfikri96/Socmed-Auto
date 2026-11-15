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


def _env_fingerprint() -> str:
    """SHA-256 of TIKTOK_REFRESH_TOKEN (never the token itself), or "" when it is not set."""
    token = os.getenv("TIKTOK_REFRESH_TOKEN", "")
    return hashlib.sha256(token.encode()).hexdigest() if token else ""


def get_valid_access_token(client_key: str, client_secret: str) -> str:
    """Return a usable access token.

    The saved token file is used unless TIKTOK_REFRESH_TOKEN has changed since the file was
    written (for example, after switching to another TikTok account). Then the file is replaced
    with a login made from the new token.
    """
    env_fp = _env_fingerprint()
    if TOKEN_FILE.exists():
        tokens = load_tokens()
        if env_fp and tokens.get("env_token_sha256") != env_fp:
            refresh_token = os.environ["TIKTOK_REFRESH_TOKEN"]
        elif tokens.get("expires_at", 0) - time.time() >= 300:
            return tokens["access_token"]
        else:
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
        # Which TIKTOK_REFRESH_TOKEN was set when this file was written, so a change can be detected.
        "env_token_sha256": _env_fingerprint(),
    }
    TOKEN_FILE.write_text(json.dumps(tokens, indent=2))
