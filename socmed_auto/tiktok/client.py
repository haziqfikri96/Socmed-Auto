"""TikTok Content Posting API v2 client."""

import math
import os
import time
from pathlib import Path

import requests

CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB per chunk

INIT_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"
STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"
USER_URL = "https://open.tiktokapis.com/v2/user/info/"


def _headers(access_token: str) -> dict:
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
    }


def get_user_info(access_token: str) -> dict:
    resp = requests.get(
        USER_URL,
        headers=_headers(access_token),
        params={"fields": "open_id,union_id,avatar_url,display_name,follower_count"},
    )
    resp.raise_for_status()
    return resp.json().get("data", {}).get("user", {})


def upload_video(
    access_token: str,
    video_path: str,
    title: str,
    hashtags: list[str],
    privacy: str = "PUBLIC_TO_EVERYONE",
    disable_comment: bool = False,
    disable_duet: bool = False,
    disable_stitch: bool = False,
) -> str:
    """Upload a video and publish it. Returns publish_id."""
    path = Path(video_path)
    file_size = path.stat().st_size
    total_chunks = math.ceil(file_size / CHUNK_SIZE)

    # Build caption (title + hashtags, max 2200 chars)
    tags = " ".join(f"#{t.lstrip('#')}" for t in hashtags)
    caption = f"{title}\n\n{tags}"[:2200]

    # 1. Init upload
    init_resp = requests.post(
        INIT_URL,
        headers=_headers(access_token),
        json={
            "post_info": {
                "title": caption,
                "privacy_level": privacy,
                "disable_duet": disable_duet,
                "disable_comment": disable_comment,
                "disable_stitch": disable_stitch,
                "video_cover_timestamp_ms": 1000,
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": file_size,
                "chunk_size": CHUNK_SIZE,
                "total_chunk_count": total_chunks,
            },
        },
    )
    init_resp.raise_for_status()
    init_data = init_resp.json().get("data", {})
    upload_url = init_data["upload_url"]
    publish_id = init_data["publish_id"]

    # 2. Upload chunks
    with open(path, "rb") as f:
        for chunk_idx in range(total_chunks):
            chunk = f.read(CHUNK_SIZE)
            start = chunk_idx * CHUNK_SIZE
            end = start + len(chunk) - 1
            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Content-Length": str(len(chunk)),
                "Content-Type": "video/mp4",
            }
            upload_resp = requests.put(upload_url, headers=headers, data=chunk)
            upload_resp.raise_for_status()

    # 3. Poll for status
    for _ in range(20):
        time.sleep(3)
        status_resp = requests.post(
            STATUS_URL,
            headers=_headers(access_token),
            json={"publish_id": publish_id},
        )
        status_resp.raise_for_status()
        status = status_resp.json().get("data", {}).get("status", "")
        if status == "PUBLISH_COMPLETE":
            return publish_id
        if status in ("FAILED", "SPAM_RISK_TOO_MANY_POSTS"):
            raise RuntimeError(f"TikTok publish failed: {status}")

    raise TimeoutError("TikTok publish timed out after 60s")
