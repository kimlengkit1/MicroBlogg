# MicroBlogg

A microservice-based blog platform built with FastAPI, featuring user authentication, blog posts, and comments. All services are containerized with Docker and communicate through an API Gateway (Nginx).

## Architecture Overview

MicroBlogg consists of four microservices, each running in its own Docker container:

### Services

- **auth-service** (Port 8000)
  - Handles user authentication (signup, login, token verification)
  - Uses JWT tokens for authentication
  - SQLite database for user storage
  - Health endpoint reports database status

- **user-service** (Port 8000)
  - Manages user profiles (display name, bio)
  - Depends on auth-service for token verification
  - SQLite database for profile storage
  - Health endpoint reports auth-service and database status

- **post-service** (Port 8000)
  - Handles blog post CRUD operations
  - Depends on auth-service for authentication
  - SQLite database for post storage
  - Health endpoint reports auth-service and database status

- **comment-service** (Port 8000)
  - Manages comments on posts
  - Depends on auth-service for authentication and post-service to verify posts exist
  - SQLite database for comment storage
  - Health endpoint reports auth-service, post-service, and database status

### Infrastructure

- **Nginx API Gateway** (Port 8080)
  - Routes all external requests to appropriate services
  - Provides unified entry point at `http://localhost:8080`
  - Load balancing ready for post-service scaling

- **Redis** (Port 6379)
  - Available for caching (currently configured but not actively used)

### Communication

- Services communicate over Docker's internal network using HTTP via `httpx`
- All services use JWT tokens issued by auth-service for authentication
- Health checks cascade: each service reports its dependencies' health status

## Prerequisites

- **Docker** (Engine 20.10+)
- **Docker Compose** (v2.0+ or integrated `docker compose` command)
- **curl** (for testing endpoints)
- **jq** (optional, for pretty JSON output)

## Installation and Setup

### 1. Clone or Extract the Project

```bash
# If using git
git clone https://github.com/kimlengkit1/MicroBlogg.git
cd MicroBlogg

# Or extract from zip file
unzip milestone1_kimlengkit.zip
cd milestone1_kimlengkit
```

### 2. Build All Services

```bash
docker compose build
```

This will build all four microservices:
- `auth-service`
- `user-service`
- `post-service`
- `comment-service`

### 3. Start All Services

```bash
docker compose up -d
```

The `-d` flag runs containers in detached mode.

### 4. Verify Services Are Running

```bash
docker compose ps
```

You should see all services with `(healthy)` status:
- `microblogg-auth-service-1`
- `microblogg-user-service-1`
- `microblogg-post-service-1`
- `microblogg-comment-service-1`
- `api-gateway` (nginx)
- `microblogg-redis-1`

### 5. Check Service Logs (Optional)

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f auth-service
docker compose logs -f user-service
docker compose logs -f post-service
docker compose logs -f comment-service
```

### 6. Stop Services

```bash
docker compose down
```

To also remove volumes (deletes all data):
```bash
docker compose down -v
```

## Usage Instructions

### Base URL

All endpoints are accessible through the API Gateway at:
```
http://localhost:8080
```

### Quick Start Example

```bash
BASE="http://localhost:8080"

# 1. Sign up
curl -X POST "$BASE/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePassword123"}'

# 2. Login and get token
TOKEN=$(curl -sS -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePassword123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 3. Create a post
curl -X POST "$BASE/posts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My First Post","body":"This is my first blog post!"}'

# 4. Create a comment
curl -X POST "$BASE/comments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"postId":"POST_ID_HERE","body":"Great post!"}'
```

## API Endpoints

### Authentication Service (`/auth`)

#### Sign Up
**POST** `/auth/signup`

Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid-string",
  "email": "user@example.com"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8080/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePassword123"}'
```

**Error Responses:**
- `409 Conflict`: Email already registered
- `422 Unprocessable Entity`: Invalid email or password format

---

#### Login
**POST** `/auth/login`

Authenticate and receive a JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8080/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePassword123"}'
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials

---

#### Verify Token
**POST** `/auth/verify`

Verify a JWT token and get user information.

**Request:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "user_id": "uuid-string",
  "email": "user@example.com"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8080/auth/verify" \
  -H "Content-Type: application/json" \
  -d '{"token":"YOUR_TOKEN_HERE"}'
```

**Error Responses:**
- `400 Bad Request`: Token required
- `401 Unauthorized`: Invalid token

---

#### Health Check
**GET** `/health` or `/auth/health`

Check service health status.

**Response (200 OK):**
```json
{
  "service": "auth-service",
  "status": "healthy",
  "dependencies": {
    "database": {
      "status": "healthy",
      "response_time_ms": 1.5,
      "error": null
    }
  }
}
```

**Example:**
```bash
curl "http://localhost:8080/health"
```

---

### User Service (`/users`)

#### Create/Update Profile
**POST** `/users/me/profile`  
**Authentication:** Required (Bearer token)

Create or update the authenticated user's profile.

**Request:**
```json
{
  "display_name": "John Doe",
  "bio": "Software developer and blogger"
}
```

**Response (201 Created):**
```json
{
  "id": "profile-uuid",
  "userId": "user-uuid",
  "display_name": "John Doe",
  "bio": "Software developer and blogger",
  "created_at": "2025-12-17T21:00:00.000Z",
  "updated_at": null
}
```

**Example:**
```bash
TOKEN="your-jwt-token-here"
curl -X POST "http://localhost:8080/users/me/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"display_name":"John Doe","bio":"Software developer"}'
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `422 Unprocessable Entity`: Validation error (display_name 1-80 chars, bio max 1000 chars)

---

#### Get User Profile by ID
**GET** `/users/{user_id}`  
**Authentication:** Not required

Get a user's profile by their user ID.

**Response (200 OK):**
```json
{
  "id": "profile-uuid",
  "userId": "user-uuid",
  "display_name": "John Doe",
  "bio": "Software developer and blogger",
  "created_at": "2025-12-17T21:00:00.000Z",
  "updated_at": null
}
```

**Example:**
```bash
curl "http://localhost:8080/users/USER_ID_HERE"
```

**Error Responses:**
- `404 Not Found`: User profile not found

---

#### Health Check
**GET** `/users/health`

Check service health status.

**Response (200 OK):**
```json
{
  "service": "user-service",
  "status": "healthy",
  "dependencies": {
    "auth-service": {
      "status": "healthy",
      "response_time_ms": 12.5,
      "error": null
    }
  }
}
```

**Example:**
```bash
curl "http://localhost:8080/users/health"
```

---

### Post Service (`/posts`)

#### Create Post
**POST** `/posts`  
**Authentication:** Required (Bearer token)

Create a new blog post.

**Request:**
```json
{
  "title": "My First Blog Post",
  "body": "This is the content of my blog post..."
}
```

**Response (201 Created):**
```json
{
  "id": "post-uuid",
  "authorId": "user-uuid",
  "title": "My First Blog Post",
  "body": "This is the content of my blog post...",
  "created_at": "2025-12-17T21:00:00.000Z",
  "updated_at": null
}
```

**Example:**
```bash
TOKEN="your-jwt-token-here"
curl -X POST "http://localhost:8080/posts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My First Post","body":"Post content here"}'
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `422 Unprocessable Entity`: Validation error (title 1-200 chars, body 1-100000 chars)

---

#### Get Post by ID
**GET** `/posts/{post_id}`  
**Authentication:** Not required

Get a post by its ID.

**Response (200 OK):**
```json
{
  "id": "post-uuid",
  "authorId": "user-uuid",
  "title": "My First Blog Post",
  "body": "This is the content of my blog post...",
  "created_at": "2025-12-17T21:00:00.000Z",
  "updated_at": null
}
```

**Example:**
```bash
curl "http://localhost:8080/posts/POST_ID_HERE"
```

**Error Responses:**
- `404 Not Found`: Post not found

---

#### List Posts
**GET** `/posts?limit={limit}&offset={offset}`  
**Authentication:** Not required

List posts with pagination.

**Query Parameters:**
- `limit` (optional): Number of posts to return (1-100, default: 50)
- `offset` (optional): Number of posts to skip (default: 0)

**Response (200 OK):**
```json
[
  {
    "id": "post-uuid",
    "authorId": "user-uuid",
    "title": "My First Blog Post",
    "body": "This is the content...",
    "created_at": "2025-12-17T21:00:00.000Z",
    "updated_at": null
  }
]
```

**Example:**
```bash
curl "http://localhost:8080/posts?limit=10&offset=0"
```

---

#### Update Post
**PUT** `/posts/{post_id}`  
**Authentication:** Required (Bearer token, must be post author)

Update a post. Only the post author can update their posts.

**Request:**
```json
{
  "title": "Updated Title",
  "body": "Updated content"
}
```
Note: Both fields are optional - include only what you want to update.

**Response (200 OK):**
```json
{
  "id": "post-uuid",
  "authorId": "user-uuid",
  "title": "Updated Title",
  "body": "Updated content",
  "created_at": "2025-12-17T21:00:00.000Z",
  "updated_at": "2025-12-17T21:05:00.000Z"
}
```

**Example:**
```bash
TOKEN="your-jwt-token-here"
curl -X PUT "http://localhost:8080/posts/POST_ID_HERE" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Title"}'
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Not the post author
- `404 Not Found`: Post not found

---

#### Delete Post
**DELETE** `/posts/{post_id}`  
**Authentication:** Required (Bearer token, must be post author)

Delete a post. Only the post author can delete their posts.

**Response (204 No Content):**

**Example:**
```bash
TOKEN="your-jwt-token-here"
curl -X DELETE "http://localhost:8080/posts/POST_ID_HERE" \
  -H "Authorization: Bearer $TOKEN"
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Not the post author
- `404 Not Found`: Post not found

---

#### Health Check
**GET** `/posts/health`

Check service health status.

**Response (200 OK):**
```json
{
  "service": "post-service",
  "status": "healthy",
  "dependencies": {
    "auth-service": {
      "status": "healthy",
      "response_time_ms": 8.5,
      "error": null
    }
  }
}
```

**Example:**
```bash
curl "http://localhost:8080/posts/health"
```

---

### Comment Service (`/comments`)

#### Create Comment
**POST** `/comments`  
**Authentication:** Required (Bearer token)

Create a comment on a post.

**Request:**
```json
{
  "postId": "post-uuid-string",
  "body": "This is my comment on the post!"
}
```

**Response (201 Created):**
```json
{
  "id": "comment-uuid",
  "postId": "post-uuid-string",
  "authorId": "user-uuid",
  "body": "This is my comment on the post!",
  "created_at": "2025-12-17T21:00:00.000Z",
  "updated_at": null
}
```

**Example:**
```bash
TOKEN="your-jwt-token-here"
curl -X POST "http://localhost:8080/comments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"postId":"POST_ID_HERE","body":"Great post!"}'
```

**Error Responses:**
- `400 Bad Request`: Post does not exist
- `401 Unauthorized`: Missing or invalid token
- `422 Unprocessable Entity`: Validation error (body 1-10000 chars)

---

#### Get Comment by ID
**GET** `/comments/{comment_id}`  
**Authentication:** Not required

Get a comment by its ID.

**Response (200 OK):**
```json
{
  "id": "comment-uuid",
  "postId": "post-uuid-string",
  "authorId": "user-uuid",
  "body": "This is my comment on the post!",
  "created_at": "2025-12-17T21:00:00.000Z",
  "updated_at": null
}
```

**Example:**
```bash
curl "http://localhost:8080/comments/COMMENT_ID_HERE"
```

**Error Responses:**
- `404 Not Found`: Comment not found

---

#### List Comments
**GET** `/comments?postId={post_id}&limit={limit}&offset={offset}`  
**Authentication:** Not required

List comments, optionally filtered by post ID.

**Query Parameters:**
- `postId` (optional): Filter comments by post ID
- `limit` (optional): Number of comments to return (1-100, default: 50)
- `offset` (optional): Number of comments to skip (default: 0)

**Response (200 OK):**
```json
[
  {
    "id": "comment-uuid",
    "postId": "post-uuid-string",
    "authorId": "user-uuid",
    "body": "This is my comment!",
    "created_at": "2025-12-17T21:00:00.000Z",
    "updated_at": null
  }
]
```

**Example:**
```bash
# List all comments
curl "http://localhost:8080/comments?limit=10&offset=0"

# List comments for a specific post
curl "http://localhost:8080/comments?postId=POST_ID_HERE&limit=10&offset=0"
```

---

#### Update Comment
**PUT** `/comments/{comment_id}`  
**Authentication:** Required (Bearer token, must be comment author)

Update a comment. Only the comment author can update their comments.

**Request:**
```json
{
  "body": "Updated comment text"
}
```

**Response (200 OK):**
```json
{
  "id": "comment-uuid",
  "postId": "post-uuid-string",
  "authorId": "user-uuid",
  "body": "Updated comment text",
  "created_at": "2025-12-17T21:00:00.000Z",
  "updated_at": "2025-12-17T21:05:00.000Z"
}
```

**Example:**
```bash
TOKEN="your-jwt-token-here"
curl -X PUT "http://localhost:8080/comments/COMMENT_ID_HERE" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"body":"Updated comment"}'
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Not the comment author
- `404 Not Found`: Comment not found

---

#### Delete Comment
**DELETE** `/comments/{comment_id}`  
**Authentication:** Required (Bearer token, must be comment author)

Delete a comment. Only the comment author can delete their comments.

**Response (204 No Content):**

**Example:**
```bash
TOKEN="your-jwt-token-here"
curl -X DELETE "http://localhost:8080/comments/COMMENT_ID_HERE" \
  -H "Authorization: Bearer $TOKEN"
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Not the comment author
- `404 Not Found`: Comment not found

---

#### Health Check
**GET** `/comments/health`

Check service health status.

**Response (200 OK):**
```json
{
  "service": "comment-service",
  "status": "healthy",
  "dependencies": {
    "auth-service": {
      "status": "healthy",
      "response_time_ms": 2.5,
      "error": null
    },
    "post-service": {
      "status": "healthy",
      "response_time_ms": 11.7,
      "error": null
    }
  }
}
```

**Example:**
```bash
curl "http://localhost:8080/comments/health"
```

---

## Testing

### Automated Test Script

A comprehensive test script is provided to test all endpoints:

```bash
bash test-all-endpoints.sh
```

This script will:
1. Test all health check endpoints
2. Test authentication (signup, login, verify)
3. Test user profile management
4. Test post CRUD operations
5. Test comment CRUD operations
6. Clean up test data

### Manual Testing Workflow

```bash
BASE="http://localhost:8080"

# 1. Sign up
curl -X POST "$BASE/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPassword123"}'

# 2. Login and get token
TOKEN=$(curl -sS -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPassword123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 3. Create profile
curl -X POST "$BASE/users/me/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"display_name":"Test User","bio":"Test bio"}'

# 4. Create a post
POST_RESPONSE=$(curl -sS -X POST "$BASE/posts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Post","body":"Post content"}')
POST_ID=$(echo "$POST_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

# 5. Create a comment
curl -X POST "$BASE/comments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"postId\": \"$POST_ID\", \"body\": \"Great post!\"}"
```

## Project Structure

```
MicroBlogg/
├── auth-service/
│   ├── app/
│   │   ├── main.py          # FastAPI app and routes
│   │   ├── models.py        # User model
│   │   ├── schemas.py       # Request/response models
│   │   ├── security.py      # Password hashing and JWT
│   │   └── db.py            # Database setup
│   ├── Dockerfile
│   └── requirements.txt
├── user-service/
│   ├── app/
│   │   ├── main.py          # FastAPI app and routes
│   │   ├── models.py        # Profile model
│   │   ├── schemas.py       # Request/response models
│   │   └── db.py            # Database setup
│   ├── Dockerfile
│   └── requirements.txt
├── post-service/
│   ├── app/
│   │   ├── main.py          # FastAPI app and routes
│   │   ├── models.py        # Post model
│   │   ├── schemas.py       # Request/response models
│   │   └── db.py            # Database setup
│   ├── Dockerfile
│   └── requirements.txt
├── comment-service/
│   ├── app/
│   │   ├── main.py          # FastAPI app and routes
│   │   ├── models.py        # Comment model
│   │   ├── schemas.py       # Request/response models
│   │   └── db.py            # Database setup
│   ├── Dockerfile
│   └── requirements.txt
├── nginx/
│   └── nginx.conf           # API Gateway configuration
├── docker-compose.yml       # Service orchestration
├── test-all-endpoints.sh    # Comprehensive test script
└── README.md                # This file
```

## Troubleshooting

### Port Already in Use

If port 8080 is already in use, change it in `docker-compose.yml`:

```yaml
nginx:
  ports:
    - "8088:80"  # Change 8080 to any free port
```

### Services Not Starting

Check service logs:
```bash
docker compose logs auth-service
docker compose logs user-service
docker compose logs post-service
docker compose logs comment-service
```

### Services Unhealthy

1. Check if all dependencies are running:
   ```bash
   docker compose ps
   ```

2. Verify health endpoints:
   ```bash
   curl http://localhost:8080/health
   curl http://localhost:8080/auth/health
   curl http://localhost:8080/users/health
   curl http://localhost:8080/posts/health
   curl http://localhost:8080/comments/health
   ```

3. Restart services:
   ```bash
   docker compose restart
   ```

### Token Verification Issues

If you get "Invalid token" errors:
1. Ensure all services use the same `AUTH_SECRET_KEY` (set in `docker-compose.yml`)
2. Check that tokens haven't expired (default: 60 minutes)
3. Verify the token format: `Authorization: Bearer <token>`

### Database Issues

If you need to reset databases:
```bash
# Stop and remove volumes
docker compose down -v

# Restart services (will create fresh databases)
docker compose up -d
```

## Environment Variables

Key environment variables (set in `docker-compose.yml`):

- `AUTH_SECRET_KEY`: JWT signing secret (must match across all services)
- `AUTH_ALGORITHM`: JWT algorithm (default: HS256)
- `AUTH_SERVICE_BASE`: Internal URL for auth-service
- `USER_SERVICE_BASE`: Internal URL for user-service
- `POST_SERVICE_BASE`: Internal URL for post-service

## License

See LICENSE file for details.

## Contributing

This is a milestone project. For issues or questions, please refer to the project documentation.
