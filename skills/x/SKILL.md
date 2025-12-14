# X Thread Posting Skill

## Overview
- Posts long text to X as a thread: main tweet + ordered replies, using a 280‑character chunk limit.
- Prefers OAuth2 user-context bearer (`X_BEARER_TOKEN` with `tweet.write`); falls back to OAuth1 (`X_API_KEY`/`X_API_KEY_SECRET` + `X_ACCESS_TOKEN`/`X_ACCESS_TOKEN_SECRET`) if bearer is absent.
- Endpoint: `https://api.x.com/2/tweets` (compatible with `api.twitter.com`).

## Credentials
- `X_BEARER_TOKEN`: OAuth2 bearer token (user context, `tweet.write`).
- OAuth1 fallback: `X_API_KEY`, `X_API_KEY_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` (requires `requests-oauthlib` installed locally).

## Usage
- Ask the model to use the skill, e.g., “Post this text to X as a thread: ...”. Tool name: `x_post_thread`.
- Returns tweet URLs in order (main tweet → replies).
