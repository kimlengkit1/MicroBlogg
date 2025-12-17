import json, os, redis

_redis = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
)

def get_json(key: str):
    val = _redis.get(key)
    return json.loads(val) if val else None

def set_json(key: str, value, ttl: int):
    _redis.setex(key, ttl, json.dumps(value))

def delete(key: str):
    _redis.delete(key)
