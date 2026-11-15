#!/usr/bin/env python3
"""Send a rendered video to your TikTok inbox as a draft: python tiktok_draft.py videos/<file>.mp4"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

from socmed_auto.tiktok.auth import get_valid_access_token
from socmed_auto.tiktok.client import get_user_info, upload_draft


def main():
    if len(sys.argv) != 2 or not os.path.isfile(sys.argv[1]):
        sys.exit("usage: python tiktok_draft.py <video.mp4>")
    key, secret = os.getenv("TIKTOK_CLIENT_KEY"), os.getenv("TIKTOK_CLIENT_SECRET")
    if not key or not secret:
        sys.exit("ERROR: TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET are not set.")

    token = get_valid_access_token(key, secret)
    print("Uploading as:", get_user_info(token).get("display_name", "unknown"))
    publish_id = upload_draft(token, sys.argv[1])
    print("Draft sent to the TikTok inbox. publish_id:", publish_id)


if __name__ == "__main__":
    main()
