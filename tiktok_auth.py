#!/usr/bin/env python3
"""
One-time TikTok login. Run this on your own computer, not in a cloud session:
TikTok sends the browser back to http://localhost:8080/callback/ on this machine.

Before running:
  1. In the TikTok developer portal, the app (or its sandbox) needs the Desktop platform,
     Login Kit with redirect URI http://localhost:8080/callback/, and Content Posting API.
  2. Put that app's Client key and Client secret in a .env file next to this script:
       TIKTOK_CLIENT_KEY=...
       TIKTOK_CLIENT_SECRET=...
  3. pip install requests python-dotenv
  4. python tiktok_auth.py
"""

import os
import secrets
import sys
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

from dotenv import load_dotenv

load_dotenv()

from socmed_auto.tiktok.auth import TOKEN_FILE, exchange_code, get_auth_url, new_code_verifier

REDIRECT_URI = "http://localhost:8080/callback/"
_result: dict = {}


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        _result.update({k: v[0] for k, v in params.items()})
        ok = "code" in params
        self.send_response(200 if ok else 400)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        msg = "Authorization successful. You can close this tab." if ok else "No code received. Check the terminal."
        self.wfile.write(f"<h2>{msg}</h2>".encode())

    def log_message(self, *_):
        pass


def main():
    client_key = os.getenv("TIKTOK_CLIENT_KEY")
    client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
    if not client_key or not client_secret:
        sys.exit("ERROR: set TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET in a .env file next to this script.")

    if TOKEN_FILE.exists():
        sys.exit(f"Already authorized. Delete {TOKEN_FILE} to log in again.")

    verifier = new_code_verifier()
    state = secrets.token_urlsafe(16)
    url = get_auth_url(client_key, REDIRECT_URI, verifier, state)

    print("Opening TikTok in your browser. If it does not open, paste this address into it:\n")
    print(url + "\n")
    print("Waiting for TikTok to send you back to http://localhost:8080 ...")
    webbrowser.open(url)

    server = HTTPServer(("localhost", 8080), CallbackHandler)
    while "code" not in _result and "error" not in _result:
        server.handle_request()

    if "error" in _result:
        sys.exit(f"ERROR from TikTok: {_result.get('error')}: {_result.get('error_description', '')}")
    if _result.get("state") != state:
        sys.exit("ERROR: the reply did not match this login attempt. Run the script again.")

    tokens = exchange_code(client_key, client_secret, _result["code"], REDIRECT_URI, verifier)
    print(f"\nSuccess. Granted: {tokens.get('scope')}")
    print(f"Tokens saved to {TOKEN_FILE} (keep this file private, never commit it).")
    print("\nFor cloud sessions, add this as TIKTOK_REFRESH_TOKEN in the environment's settings:")
    print(f"\n  {tokens.get('refresh_token')}\n")


if __name__ == "__main__":
    main()
