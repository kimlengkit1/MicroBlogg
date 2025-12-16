FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# SQLite db folder
RUN mkdir -p /app/data
COPY app/ ./app/

ENV DATABASE_URL=sqlite:///data/auth.db
ENV AUTH_SECRET_KEY=dev-secret-change-me
ENV AUTH_ALGORITHM=HS256
ENV ACCESS_TOKEN_EXPIRE_MINUTES=60

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]