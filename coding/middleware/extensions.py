import os
import redis
from flask_jwt_extended import JWTManager

redis_client = redis.Redis(
        host = os.getenv("REDIS_HOST", "localhost"),
        port = int(os.getenv("REDIS_PORT", 6379)),
        db = int(os.getenv("REDIS_DB", 0)),
        decode_responses = True
        )

try: 
    redis_client.ping()
    print("Redis connection successful")
except redis.ConnectionError as e:
    raise RuntimeError("Failed to connect to Redis") from e

