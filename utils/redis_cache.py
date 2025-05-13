import redis
from utils.logger import log_error

def initialize_redis():
    """Initialize Redis client."""
    try:
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        return redis_client
    except Exception as e:
        log_error(f"Redis init error: {str(e)}")
        return None
