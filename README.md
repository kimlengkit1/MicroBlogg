# MicroBlogg
Microservice blog platform built with FastAPI. Its core features are a post service for creating and managing blogs, a comment service for threaded discussions, and a user authentication service for sign up, log in, and access control.

## Architecture Overview

There are four FastAPI services, each running in its own container:

- **auth-service**
    - Responsible for authentications, login, sign up
    - `GET /health` with its own status.
- **user-service**
    - Responsible for profile displays and editing
    - `GET /health` calls `auth-service /health` and reports both its own status and `auth-service` as a dependency.
- **post-service**
    - Responsible for blog posts features
    - GET /health` calls `auth-service /health` and `user-service /health` and reports their statuses.
- **comment-service**
    - Responsible for comments on posts
    - `GET /health` calls `user-service /health` and `post-service /health` and reports their statuses.

All services communicate over an internal Docker network using HTTP via `httpx`.

## Prerequisites

- **Docker** (Engine)
- **Docker Compose** (v2 or integrated `docker compose` command)

For running locally without Docker:

- **Python** 3.11+
- `pip` for installing Python dependencies

## Installation and Setup

You can get this application via GitHub or via a zip file:

**Zip File**

unzip the milestone1_kimlengkit.zip
```Terminal
cd milestone1_kimlengkit.zip
```

**Clone the repository from GitHub**

```Terminal
git clone <https://github.com/kimlengkit1/MicroBlogg.git>
cd MICROBLOGG
```

**Build the services**

```Terminal
docker compose build
```

**Start all services**

```Terminal
docker compose up -d
```

**Verify containers are running**

```Terminal
docker compose ps
```

Check for contains:
- `auth-service`
- `user-service`
- `post-service`
- `comment-service`

**To View logs**

```Terminal
docker compose logs -f
```

## Usage Instructions

### Starting the System

From the project root:

```Terminal
docker compose up -d --build
```

Check that the containers are healthy

```Terminal
docker compose ps
```
You should see `auth-service`, `user-service`, `post-service`, `comment-service`, and `api-gateway` (nginx) up and running. We won't be needing the `redis` and `api-gateway` for the `/health` endpoints currently. It is for later implementation of the project.

### Health Check Endpoints

Each service exposes a health endpoint:
- `auth-service`: `GET /health`
- `user-service`: `GET /health`
- `post-service`: `GET /health`
- `comment-service`: `GET /health`

Call them directly using `docker compose exec`:

## Auth-service health
```Terminal
docker compose exec auth-service curl http://localhost:8000/health
```
or

```Terminal
docker compose exec auth-service curl http://localhost:8000/auth/health
```

### Nginx

```Terminal
  curl -sS -i http://localhost:8080/auth/health
```


status `"healthy"` with HTTP code `200`:

```JSON
{
  HTTP/1.1 200 OK
  date: Tue, 16 Dec 2025 18:26:53 GMT
  server: uvicorn
  content-length: 145
  content-type: application/json

  {"service":"auth-service","status":"healthy","dependencies": {"database":     {"status":"healthy","response_time_ms":1.7119169933721423,"error":null}}}
  }
```

or 

```JSON
{
  HTTP/1.1 200 OK
  Server: nginx/1.29.3
  Date: Tue, 16 Dec 2025 18:27:41 GMT
  Content-Type: application/json
  Content-Length: 144
  Connection: keep-alive
}
```

## Auth-service Sign up/Login

Sign up:
```Terminal
  docker compose exec auth-service sh -lc 'curl -sS -i -X POST http://localhost:8000/auth/signup -H "Content-Type: application/json" -d "{\"email\":\"alice2@example.com\",\"password\":\"CorrectHorseBatteryStaple\"}"'
```

Replace the email field or password file with the email and password you want to sign up with. It should return `HTTP/1.1 201 Created` if successful:

```JSON
{
  HTTP/1.1 201 Created
  date: Tue, 16 Dec 2025 18:27:06 GMT
  server: uvicorn
  content-length: 37
  content-type: application/json

  {"id":1,"email":"alice2@example.com"}
}
```

Login:

```Terminal
docker compose exec auth-service sh -lc \
'curl -sS -i -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d "{\"email\":\"alice2@example.com\",\"password\":\"CorrectHorseBatteryStaple\"}"'
```
Return `HTTP/1.1 201 OK` if successful:

```JSON
{
  HTTP/1.1 200 OK
  date: Tue, 16 Dec 2025 18:27:13 GMT
  server: uvicorn
  content-length: 182
  content-type: application/json

  {"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzY1OTA5NjM0LCJleHAiOjE3NjU5MTMyMzR9.pbKpLa5P5pmDheFufq7dMGnBKhCwaoy7W3yScdIeiLw","token_type":"bearer"}
}
```

### Nginx:

Sign Up:

```Terminal
curl -sS -i -X POST http://localhost:8080/auth/signup -H "Content-Type: application/json" -d '{"email":"alice3@example.com","password":"CorrectHorseBatteryStaple"}'
```

Return `HTTP/1.1 201 Created` if successful:

```JSON
{
  HTTP/1.1 201 Created
  Server: nginx/1.29.3
  Date: Tue, 16 Dec 2025 18:27:49 GMT
  Content-Type: application/json
  Content-Length: 37
  Connection: keep-alive

  {"id":2,"email":"alice3@example.com"}
}
```
Login:

```Terminal
curl -sS -i -X POST http://localhost:8080/auth/login -H "Content-Type: application/json" -d '{"email":"alice3@example.com","password":"CorrectHorseBatteryStaple"}'
```
Return `HTTP/1.1 201 OK` if successful:

```JSON
{
  HTTP/1.1 200 OK
  Server: nginx/1.29.3
  Date: Tue, 16 Dec 2025 18:27:55 GMT
  Content-Type: application/json
  Content-Length: 182
  Connection: keep-alive

{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiaWF0IjoxNzY1OTA5Njc1LCJleHAiOjE3NjU5MTMyNzV9.TXEZYOS7DGgPQY2o9lZK5oWxRHqFKsWJBq3UalskdYI","token_type":"bearer"}
}
```


### User-service health

```Terminal
docker compose exec user-service curl -sS -i http://localhost:8000/health
```
or
```Terminal
docker compose exec user-service curl -sS -i http://localhost:8000/users/health
```

status `"healthy"` with HTTP code `200`:

```JSON
{
  HTTP/1.1 200 OK
  date: Tue, 16 Dec 2025 19:02:37 GMT
  server: uvicorn
  content-length: 148
  content-type: application/json

  {"service":"user-service","status":"healthy","dependencies":{"auth-service":{"status":"healthy","response_time_ms":11.68166595743969,"error":null}}}
}
```
status `"unhealthy"` with HTTP code `503`.

### Via Nginx:

```Terminal
curl -sS -i http://localhost:8080/users/health
```

If successful:

```JSON
{
  HTTP/1.1 200 OK
  Server: nginx/1.29.3
  Date: Tue, 16 Dec 2025 19:02:51 GMT
  Content-Type: application/json
  Content-Length: 149
  Connection: keep-alive

  {"service":"user-service","status":"healthy","dependencies":{"auth-service":{"status":"healthy","response_time_ms":18.958040978759527,"error":null}}}
}
```

## User-service Profile

Create an account if an account doesn't exist:

```Terminal
curl -sS -X POST http://localhost:8080/auth/signup -H "Content-Type: application/json" -d '{"email":"bob@example.com","password":"CorrectHorseBatteryStaple"}'
{"id":3,"email":"bob@example.com"}
```
Login and get the TOKEN access key:

```Terminal
TOKEN=$(curl -sS -X POST http://localhost:8080/auth/login -H "Content-Type: application/json" -d '{"email":"bob@example.com","password":"CorrectHorseBatteryStaple"}' | python3 -c 'import sys, json; print(json.load(sys.stdin)["access_token"])')
echo "$TOKEN"
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiaWF0IjoxNzY1OTExODk4LCJleHAiOjE3NjU5MTU0OTh9.5CRqRBPPVBTXRpuhhJ7fyKmst-iNrdjDaRrpBRwD1gU
```

Check account:

```Terminal
curl -sS -i http://localhost:8080/users/me
```

If successful:

```JSON
{
  HTTP/1.1 200 OK
  Server: nginx/1.29.3
  Date: Tue, 16 Dec 2025 19:07:09 GMT
  Content-Type: application/json
  Content-Length: 56
  Connection: keep-alive

  {"id":1,"auth_user_id":3,"display_name":null,"bio":null}
}
```

Edit Profile:

```Terminal
curl -sS -i -X PUT http://localhost:8080/users/me -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"display_name":"Bob B.","bio":"I like distributed systems."}'
```

If successful:

```JSON
{
  HTTP/1.1 200 OK
  Server: nginx/1.29.3
  Date: Tue, 16 Dec 2025 19:08:00 GMT
  Content-Type: application/json
  Content-Length: 85
  Connection: keep-alive

  {"id":1,"auth_user_id":3,"display_name":"Bob B.","bio":"I like distributed systems."}
}
```

Profile Lookup by id:

```Terminal
curl -sS -i http://localhost:8080/users/1
```

If successful:

```JSON
{
  HTTP/1.1 200 OK
  Server: nginx/1.29.3
  Date: Tue, 16 Dec 2025 19:08:18 GMT
  Content-Type: application/json
  Content-Length: 85
  Connection: keep-alive
  
  {"id":1,"auth_user_id":3,"display_name":"Bob B.","bio":"I like distributed systems."}
}
```
### post-service health
```Terminal
docker compose exec post-service curl http://localhost:8000/health
```
status `"healthy"` with HTTP code `200`:

```JSON
{
  "service": "post-service",
  "status": "healthy",
  "dependencies": {
    "auth-service": {
      "status": "healthy",
      "response_time_ms": 10.1,
      "error": null
    },
    "user-service": {
      "status": "healthy",
      "response_time_ms": 13.4,
      "error": null
    }
  }
}
```

status `"unhealthy"` with HTTP code `503`:
```JSON
{
  "service": "post-service",
  "status": "unhealthy",
  "dependencies": {
    "auth-service": {
      "status": "unhealthy",
      "response_time_ms": 201.9,
      "error": "ConnectTimeout: GET http://auth-service:8000/health timed out"
    },
    "user-service": {
      "status": "healthy",
      "response_time_ms": 12.7,
      "error": null
    }
  }
}
```

comment-service health
```Terminal
docker compose exec comment-service curl http://localhost:8000/health
```
status `"healthy"` with HTTP code `200`:

```JSON
{
  "service": "comment-service",
  "status": "healthy",
  "dependencies": {
    "user-service": {
      "status": "healthy",
      "response_time_ms": 9.8,
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
status `"unhealthy"` with HTTP code `503`:

```JSON
{
  "service": "comment-service",
  "status": "unhealthy",
  "dependencies": {
    "user-service": {
      "status": "healthy",
      "response_time_ms": 11.4,
      "error": null
    },
    "post-service": {
      "status": "unhealthy",
      "response_time_ms": 48.3,
      "error": "HTTPStatusError: 503 from /health"
    }
  }
}

```

If a dependency is unhealthy or unreachable, the `status` field will be `"unhealthy"` and the HTTP status code will be `503`. Otherwise, the `status` is `"healthy"` and the HTTP status code will be `200`.

## Posting Service

1. Create an account.
2. Login 
3. Post services (writes require JWT)

```Terminal
# create
NEW_POST=$(
  curl -sS -X POST $BASE/posts \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"title":"Hello","body":"My first blog post"}'
)
echo "$NEW_POST" | jq .
POST_ID=$(echo "$NEW_POST" | jq -r .id)
echo "POST_ID=$POST_ID"

# get by id
curl -sS $BASE/posts/$POST_ID | jq .

# list (should include the new one)
curl -sS "$BASE/posts?limit=20&offset=0" | jq .

# update title
curl -sS -X PUT $BASE/posts/$POST_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Hello v2"}' | jq .

# delete
curl -sS -X DELETE $BASE/posts/$POST_ID \
  -H "Authorization: Bearer $TOKEN" -i
echo; echo "verify 404 after delete:"
curl -sS -i $BASE/posts/$POST_ID | sed -n '1,1p'

```

### Stopping the System

```Terminal
docker compose down
```

## Testing

The system can be tested manually through `curl` or any HTTP client (example: browser).

Confirm that each service responds to `/health` by including in the terminal:

```Terminal
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

Simulate failures by stopping one service and check how its dependents respond:

```Terminal
docker compose stop auth-service
```

user-service should now report auth-service as unhealthy
```Terminal
curl http://localhost:8002/health
```

user-service should now also be unhealthy
```Terminal
curl http://localhost:8003/health
```

Restart the service:
```Terminal
docker compose start auth-service
```

## Project Structure

```text
MICROBLOGG (milestone1_kimlengkit)/
├── auth-service/
│   ├── app/
│   │   ├── health_models.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── comment-service/
│   ├── app/
│   │   ├── health_models.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── nginx/
│   └── nginx.conf
├── post-service/
│   ├── app/
│   │   ├── health_models.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── user-service/
│   ├── app/                      
│   ├── Dockerfile
│   └── requirements.txt
├── .gitignore
├── architecture-diagram.md       
├── architecture-diagram.png      
├── architecture-document.md       
├── CODE_PROVENANCE.md
├── docker-compose.yml
├── LICENSE
└── README.md
```

- `*-service/app/main.py` is where FastAPI app expose `GET /health`
- `*-service/app/health_models.py` is the Pydantic models for `HealthResponse`, `DependencyHealth`, and `Status`
- `*-service/app/requirements.txt` is the dependencies that the service requires
- `*-service/app/Dockerfile` is the container build for each service
- `docker-compose.yml` orchestrates services on a shared Docker network
- `nginx/nginx.conf` the API gateway
- `architecture-diagram.md/.png` is a visual of health-check interactions
- `architecture-document.md` is the system architecture document 
- `CODE_PROVENANCE.md` is the prompts/tools where AI outputs were used and non-AI sources

## Troubleshooting

- If port 8080 is already in use, use 8088:80 in docker-compose.yml or any free port
- If service(s) is/are unhealthy: run ```Terminal
docker compose logs --tail=200 <service>``` to see the startup errors
  - Verify `uvicorn app.main:app`, `/health` route, and `curl` are available for the healthcheck
