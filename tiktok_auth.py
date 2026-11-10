#!/usr/bin/env python3
"""
One-time TikTok OAuth setup.

Run this once on your computer to authorize your TikTok account.
After completing this, the tokens are saved and auto_post.py handles everything.

Steps:
  1. Create a TikTok Developer App at https://developers.tiktok.com
  2. Enable "Content Posting API" for your app
  3. Set Redirect URI to: http://localhost:8080/callback
  4. Copy your Client Key and Client Secret to .env
  5. Run: python tiktok_auth.py
"""

import os
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

from dotenv import load_dotenv

load_dotenv()

from socmed_auto.tiktok.auth import exchange_code, get_auth_url, load_tokens

REDIRECT_URI = "http://localhost:8080/callback"
_auth_code: str | None = None


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            _auth_code = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h2>Authorization successful! You can close this tab.</h2>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<h2>No code received. Try again.</h2>")

    def log_message(self, *_):
        pass


def main():
    client_key = os.getenv("TIKTOK_CLIENT_KEY")
    client_secret = os.getenv("TIKTOK_CLIENT_SECRET")

    if not client_key or not client_secret:
        print("ERROR: Set TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET in your .env file.")
        print("\nGet them from: https://developers.tiktok.com")
        sys.exit(1)

    # Check if already authorized
    try:
        tokens = load_tokens()
        print(f"Already authorized! Open ID: {tokens.get('open_id', 'unknown')}")
        print("Delete .tiktok_tokens.json to re-authorize.")
        return
    except FileNotFoundError:
        pass

    url = get_auth_url(client_key, REDIRECT_URI)
    print("=" * 60)
    print("Open this URL in your browser to authorize TikTok:")
    print()
    print(url)
    print()
    print("Waiting for callback on http://localhost:8080 ...")
    print("=" * 60)

    server = HTTPServer(("localhost", 8080), CallbackHandler)
    server.handle_request()

    if not _auth_code:
        print("ERROR: No auth code received.")
        sys.exit(1)

    tokens = exchange_code(client_key, client_secret, _auth_code, REDIRECT_URI)
    print(f"\nSuccess! Authorized as open_id: {tokens.get('open_id')}")
    print("Tokens saved to .tiktok_tokens.json")
    print("\nNow run:  python auto_post.py --dry-run")


if __name__ == "__main__":
    main()
