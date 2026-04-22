#!/usr/bin/env bash
set -euo pipefail

BASE="http://localhost:8080"
EMAIL="testcomment@example.com"
PASS="testpass123"

echo "=== Testing Comment Creation ==="
echo ""

# Sign up
echo "1. Signing up user..."
SIGNUP_RESPONSE=$(curl -sS -X POST "$BASE/auth/signup" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}" || echo "{}")
echo "Signup response: $SIGNUP_RESPONSE"
echo ""

# Login
echo "2. Logging in..."
LOGIN_RESPONSE=$(curl -sS -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
  TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
  echo "✓ Login successful"
  echo "Token: ${TOKEN:0:30}..."
else
  echo "✗ Login failed: $LOGIN_RESPONSE"
  exit 1
fi
echo ""

# Test verify endpoint
echo "3. Testing auth verify endpoint..."
VERIFY_RESPONSE=$(curl -sS -X POST "$BASE/auth/verify" \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$TOKEN\"}")
if echo "$VERIFY_RESPONSE" | grep -q "user_id"; then
  echo "✓ Verify endpoint works"
  echo "$VERIFY_RESPONSE" | python3 -m json.tool
else
  echo "✗ Verify failed: $VERIFY_RESPONSE"
  exit 1
fi
echo ""

# Create a post
echo "4. Creating a post..."
POST_RESPONSE=$(curl -sS -X POST "$BASE/posts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Post for Comments","body":"This post is for testing comments"}')

if echo "$POST_RESPONSE" | grep -q "id"; then
  POST_ID=$(echo "$POST_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
  echo "✓ Post created with ID: $POST_ID"
else
  echo "✗ Post creation failed: $POST_RESPONSE"
  exit 1
fi
echo ""

# Create a comment
echo "5. Creating a comment..."
COMMENT_RESPONSE=$(curl -sS -X POST "$BASE/comments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"postId\": \"$POST_ID\", \"body\": \"This is a test comment!\"}")

if echo "$COMMENT_RESPONSE" | grep -q "id"; then
  COMMENT_ID=$(echo "$COMMENT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
  echo "✓ Comment created successfully!"
  echo "Comment ID: $COMMENT_ID"
  echo "Full response:"
  echo "$COMMENT_RESPONSE" | python3 -m json.tool
else
  echo "✗ Comment creation failed: $COMMENT_RESPONSE"
  exit 1
fi
echo ""

# Get the comment
echo "6. Retrieving the comment..."
GET_COMMENT=$(curl -sS "$BASE/comments/$COMMENT_ID")
if echo "$GET_COMMENT" | grep -q "id"; then
  echo "✓ Comment retrieved successfully:"
  echo "$GET_COMMENT" | python3 -m json.tool
else
  echo "✗ Failed to retrieve comment: $GET_COMMENT"
  exit 1
fi
echo ""

echo "=== All tests passed! ==="

