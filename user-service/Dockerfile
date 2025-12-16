FROM python:3.11-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/data
COPY app/ ./app/

ENV DATABASE_URL=sqlite:///data/user.db
ENV AUTH_SERVICE_BASE=http://auth-service:8000
ENV AUTH_SECRET_KEY=dev-secret-change-me
ENV AUTH_ALGORITHM=HS256

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
