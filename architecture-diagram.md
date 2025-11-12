```mermaid
flowchart TB
    Client[Client/Browser]

    subgraph Docker_Network[Microservice Blog - Docker Network]
        A[auth-service<br/>GET /health]
        U[user-service<br/>GET /health]
        P[post-service<br/>GET /health]
        C[comment-service<br/>GET /health]
    end

    %% Client -> services
    Client -->|GET /health| A
    Client -->|GET /health| U
    Client -->|GET /health| P
    Client -->|GET /health| C

    %% Service-to-service health checks
    U -->|httpx GET /health| A
    P -->|httpx GET /health| A
    P -->|httpx GET /health| U
    C -->|httpx GET /health| U
    C -->|httpx GET /health| P
