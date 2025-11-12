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
You should see `auth-service`, `user-service`, `post-service`, `comment-service`, `redis`, and `api-gateway` (nginx) up and running. We won't be needing the `redis` and `api-gateway` for the `/health` endpoints currently. It is for later implementation of the project.

### Health Check Endpoints

Each service exposes a health endpoint:
- `auth-service`: `GET /health`
- `user-service`: `GET /health`
- `post-service`: `GET /health`
- `comment-service`: `GET /health`

Call them directly using `docker compose exec`:

### auth-service health
```Terminal
docker compose exec auth-service curl http://localhost:8000/health
```

status `"healthy"` with HTTP code `200`:

```JSON
{
  "service": "post-service",
  "status": "healthy",
  "dependencies": {}
}
```

```
### user-service health
```Terminal
docker compose exec user-service curl http://localhost:8000/health
```

status `"healthy"` with HTTP code `200`:

```JSON
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

status `"unhealthy"` with HTTP code `503`:

```JSON
{
  "service": "user-service",
  "status": "unhealthy",
  "dependencies": {
    "auth-service": {
      "status": "unhealthy",
      "response_time_ms": 50.3,
      "error": "HTTPError or connection error details..."
    }
  }
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