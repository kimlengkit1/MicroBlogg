# System Architecture Document

## System Purpose

This system is a microservice blog platform prototype. It supports core blogging features such as user accounts, posts, and comments. Currently, it supports **health monitoring architecture** across multiple services.

Each service exposes a `/health` endpoint that reports its own status and the status of its dependencies. This allows other services or the client to quickly determine whether the system is functioning correctly and which component is failing when there is a problem.

### Problem it solves:

Important information often get scattered everywhere. Even if there is a single site for that service, when there are many people using the site at the same time, it becomes slow, unreliable, and could crash, making it difficult for people to stay informed.

The microservice blog platform gives people a place to share stories, ideas, and information in one space. People can announce event updates, post articles, and connect with the community.

The design helps keep growing blog platform more dependable and easy to fix as it gets more features and more users. Instead of cramming everything into one big system, it separates logins, profiles, posts, and comments into their own parts. 


## Service Boundaries

The system is separated into four FastAPI microservices with only the health endpoints being implemented currently.

- **auth-service**: 
    - Responsible for authentication and identifying users. It would eventually be able to handle login, token issuance, and validation. For health check, it is the base dependency for other services. If the health check for auth-service fails, the other services will also be `"unhealthy"`.
    - Multiple services rely on `auth-service`, so keeping it isolated makes it easier to make changes to authentication, tokens, or security policies without having to redeploy user, post, or comment logic.

- **user-service**: 
    - Responsible for user profiles and user-related data. It depends on `auth-service` because user information depends on verified users. Its `/health` reports both its own status and  `auth-service` status, and if any of the services it depends on fail, its own health check will be reported as failed.
    - User data is different from authentication and blog content. Separating it lets us change profile-related information independently without having to redeploy auth or content.

- **post-service**: 
    - Responsible for blog posts (creating, listing, and managing posts). It depends on `auth-service` to ensure that only verified users can create or modify posts, and on `user-service` to associate posts with the correct user accounts. If any of the services it depends on fail, its own health check will be reported as failed.
    - The post service is high-traffic and content-focused. Separating it allow us to scale it more independently (more replicas for read-heavy traffic) without affecting auth, user, or comment services.

- **comment-service**: 
    - Responsible for comments associated with posts. It depends on `user-service` to validate the commenting user and `post-service` to validate the target post before accepting or updating a comment. Its `/health` reports both its own status and the status of `user-service` and `post-service`, and if any of the services it depends on fail, its own health check will be reported as failed.
    - This depends on users and posts, but it can grow at a different rate (there can be more comments than posts). We want to be able to independently scale comment service without overloading the post or user services.

## Data Flow

The health-check data flow is focused around `/health` endpoints:

1. A client (browser, curl, other tools) sends `GET /health` requests directly to any service:
    - `auth-service /health`
    - `user-service /health`
    - `post-service /health`
    - `comment-service /health`

2. When `user-service /health` is called:
    - Computes its own status
    - Sends an internal HTTP request to `auth-service /health`
    - Combines `auth-service` status and response time into its `dependencies` field

3. 3. When `post-service /health` is called:
    - Computes its own status
    - Sends internal HTTP requests to:
        - `auth-service /health`
        - `post-service /health`
    - Combines their statuses and response times into its `dependencies`

4. 3. When `comment-service /health` is called:
    - Computes its own status
    - Sends internal HTTP requests to:
        - `user-service /health`
        - `post-service /health`
    - Combines their statuses and response times into its `dependencies`

5. Each service returns a JSON payload in the form:

```json
{
    "service": "service-name",
     "status": "healthy",
     "dependencies": {
       "other-service": {
         "status": "healthy",
         "response_time_ms": 15.2,
         "error": null
       }
     }
}
```

If any dependency is unhealthy or unreachable, the top-level `status` becomes `"unhealthy"` and the HTTP status code is `503`. Otherwise, it is `"healthy"` with HTTP status `200`.

## Communication Patterns

The communication for health monitoring in the blog platform is over **synchronous HTTP** calls over the internal Docker network:
- Each service exposes a RESTful `GET /health` endpoint.
- Services that depends on others (user, post, comment) use `httpx` to make internal HTTP requests to other services' `/health` endpoints.
    - `user-service` -> `auth-service`
    - `post-service` -> `auth-service` and `user-service`
    - `comment-service` -> `user-service` and `post-service`

The downstream health services allows higher-level components to understand the status of their full dependency chain. For this milestone, I did not use API gateway, so the client talks directly to each service, and services talk directly to each other over the Docker network.

## Technology Stack
- **Python 3.11**: It has an ecosystem for web APIs and async IO.
- **FastAPI**: 
    - Used to implement each micro services
    - Easy declaration of HTTP endpoints (for instance `/health`)
    - Automatic JSON serialization
    - Integration with Pydantic for typed models
- **Pydantic (v2)**: Used to define the health response models (`HealthResponse` and `DependencyHealth`). It helps ensure consistent JSON structure, type safety, and easy health data validation.
- **httpx**: Used for service-to-service communication in health checks. It supports async HTTP calls, timeouts, and error handling.
- **Docker and Docker Compose**: Used to containerize each service and run them together on the shared network. It mirror real microservice deployments and make it easier to bring up the whole system.
