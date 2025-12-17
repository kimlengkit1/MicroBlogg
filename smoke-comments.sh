#!/usr/bin/env bash
set -euo pipefail

BASE="http://localhost:8080"

say() { printf "\n %s\n" "$*"; }

curl_json() {
  local out
  out=$(curl -sS -f "$@")
  if command -v jq >/dev/null 2>&1; then
    echo "$out" | jq .
  else
    echo "$out"
  fi
}

# Health checks

say "Gateway health"
curl -sS -i "$BASE/health" | head -n 1

say "Auth service health (via NGINX)"
curl_json "$BASE/auth/health"

say "Post service health (via NGINX)"
curl_json "$BASE/posts/health" || true   # ok if you only exposed /health root

say "Comment service health (via NGINX)"
curl_json "$BASE/comments/health" || true  # ok if you only exposed /health root

# Also directly from inside containers (optional)
say "Comment service health (direct in container)"
docker compose exec -T comment-service curl -sS -f http://localhost:8000/health | { command -v jq >/dev/null && jq . || cat; }


# Sign up (idempotent)
EMAIL="commenter@example.com"
PASS="CorrectHorseBatteryStaple"

say "Sign up commenter (idempotent; ignore 'already registered')"
curl -sS -X POST "$BASE/auth/signup" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}" || true


# Login and capture token
say "Login to fetch JWT"
LOGIN_JSON=$(curl -sS -f -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}")

if command -v jq >/dev/null 2>&1; then
  TOKEN=$(echo "$LOGIN_JSON" | jq -r .access_token)
else
  TOKEN=$(python3 - <<'PY'
import sys, json
print(json.load(sys.stdin)["access_token"])
PY
<<<"$LOGIN_JSON")
fi

echo "TOKEN prefix: ${TOKEN:0:20}…"

# Create a post (needed to attach comments)
say "Create a post to comment on"
NEW_POST_JSON=$(curl -sS -f -X POST "$BASE/posts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Comment playground","body":"Post to test comment CRUD"}')

if command -v jq >/dev/null 2>&1; then
  POST_ID=$(echo "$NEW_POST_JSON" | jq -r .id)
else
  POST_ID=$(python3 - <<'PY'
import sys, json
print(json.load(sys.stdin)["id"])
PY
<<<"$NEW_POST_JSON")
fi
echo "POST_ID=$POST_ID"

# Create a comment
say "Create a comment"
NEW_COMMENT_JSON=$(curl -sS -f -X POST "$BASE/comments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"postId\": \"$POST_ID\", \"body\": \"First! 🎉\"}")

if command -v jq >/dev/null 2>&1; then
  echo "$NEW_COMMENT_JSON" | jq .
  COMMENT_ID=$(echo "$NEW_COMMENT_JSON" | jq -r .id)
else
  echo "$NEW_COMMENT_JSON"
  COMMENT_ID=$(python3 - <<'PY'
import sys, json
print(json.load(sys.stdin)["id"])
PY
<<<"$NEW_COMMENT_JSON")
fi
echo "COMMENT_ID=$COMMENT_ID"

# Get the comment by id
say "Read comment by id"
curl_json "$BASE/comments/$COMMENT_ID"


# List comments for the post
say "List comments for the post"
curl_json "$BASE/comments?post_id=$POST_ID&limit=10&offset=0"


# Update the comment
say "Update comment body"
curl_json -X PUT "$BASE/comments/$COMMENT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"body":"Edited body ✏️"}'

# Delete the comment
say "Delete comment"
curl -sS -i -X DELETE "$BASE/comments/$COMMENT_ID" \
  -H "Authorization: Bearer $TOKEN" | head -n 1

say "Verify it is gone (expect 404)"
curl -sS -i "$BASE/comments/$COMMENT_ID" | head -n 1

# Final health ping
say "Final comment health check"
curl_json "$BASE/comments/health" || curl_json "$BASE/health"
