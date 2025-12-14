import os
from typing import Dict, List

import requests

MAX_TWEET_CHARS = 280
API_URL = "https://api.x.com/2/tweets"  # fallback domain also works: https://api.twitter.com/2/tweets


def _chunk_text(text: str, limit: int = MAX_TWEET_CHARS) -> List[str]:
    """Split text into chunks <= limit. If a single token exceeds limit, hard-split it."""
    cleaned = " ".join(text.split())  # collapse whitespace/newlines
    words = cleaned.split(" ")
    chunks: List[str] = []
    current = ""
    for w in words:
        # if token itself longer than limit, split it
        while len(w) > limit:
            head, w = w[:limit], w[limit:]
            if current:
                chunks.append(current)
                current = ""
            chunks.append(head)
        if not current:
            current = w
        elif len(current) + 1 + len(w) <= limit:
            current += " " + w
        else:
            chunks.append(current)
            current = w
    if current:
        chunks.append(current)
    return chunks if chunks else [""]


def _post_tweet(text: str, bearer_token: str = None, in_reply_to: str = None, oauth1=None) -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    payload: Dict[str, object] = {"text": text}
    if in_reply_to:
        payload["reply"] = {"in_reply_to_tweet_id": in_reply_to}

    resp = requests.post(API_URL, headers=headers, json=payload, timeout=15, auth=oauth1)
    if not resp.ok:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise RuntimeError(f"Tweet post failed: {resp.status_code} {detail}")
    data = resp.json().get("data", {})
    return {"id": data.get("id"), "text": data.get("text")}


def handle(
    text: str,
    bearer_token: str = None,
    api_key: str = None,
    api_key_secret: str = None,
    access_token: str = None,
    access_token_secret: str = None,
) -> Dict[str, object]:
    """
    Post text as a thread. Returns posted tweet ids and URLs.

    Args:
        text: The full text to post.
        bearer_token: Optional; if not provided, uses env X_BEARER_TOKEN.
        api_key/api_key_secret/access_token/access_token_secret: Optional OAuth1 creds (fallback).
    """
    token = bearer_token or os.environ.get("X_BEARER_TOKEN")
    oauth1 = None

    # Prefer OAuth1 user context; if not provided, fall back to bearer.
    api_key = api_key or os.environ.get("X_API_KEY")
    api_key_secret = api_key_secret or os.environ.get("X_API_KEY_SECRET")
    access_token = access_token or os.environ.get("X_ACCESS_TOKEN")
    access_token_secret = access_token_secret or os.environ.get("X_ACCESS_TOKEN_SECRET")

    if all([api_key, api_key_secret, access_token, access_token_secret]):
        try:
            from requests_oauthlib import OAuth1  # type: ignore
        except Exception as e:
            raise RuntimeError(f"OAuth1 requires requests-oauthlib: {e}")
        oauth1 = OAuth1(api_key, api_key_secret, access_token, access_token_secret)
        token = None  # use OAuth1 for auth

    if not token and oauth1 is None:
        raise RuntimeError("Missing credentials. Provide OAuth1 keys (X_API_KEY/_SECRET + X_ACCESS_TOKEN/_SECRET) or bearer_token/X_BEARER_TOKEN.")

    parts = _chunk_text(text, MAX_TWEET_CHARS)
    posted = []
    reply_to = None
    for part in parts:
        tweet = _post_tweet(part, bearer_token=token, in_reply_to=reply_to, oauth1=oauth1)
        reply_to = tweet["id"]
        posted.append(tweet)

    base_url = "https://x.com/i/web/status/"
    return {
        "tweets": posted,
        "urls": [base_url + t["id"] for t in posted if t.get("id")],
    }


# Tool schema for auto-registration
tool = {
    "type": "function",
    "function": {
        "name": "x_post_thread",
        "description": "Post text to X (Twitter) as a thread, splitting over 280 chars and chaining replies.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Full text to post."},
                "bearer_token": {
                    "type": "string",
                    "description": "OAuth2 bearer token with tweet.write scope. If omitted, uses env X_BEARER_TOKEN.",
                },
                "api_key": {"type": "string", "description": "OAuth1 API key (fallback if no bearer)."},
                "api_key_secret": {"type": "string", "description": "OAuth1 API key secret (fallback if no bearer)."},
                "access_token": {"type": "string", "description": "OAuth1 access token (fallback if no bearer)."},
                "access_token_secret": {"type": "string", "description": "OAuth1 access token secret (fallback if no bearer)."},
            },
            "required": ["text"],
        },
    },
}


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python x_post.py \"your text\"")
        raise SystemExit(1)
    txt = sys.argv[1]
    print(handle(txt))
