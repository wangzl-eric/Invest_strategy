"""Redis caching layer for metrics, market data, and API responses."""
import json
import logging
import hashlib
from typing import Optional, Any, Union
from datetime import timedelta
from functools import wraps

try:
    import redis
    from redis.exceptions import ConnectionError, TimeoutError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages Redis caching operations."""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        self.enabled = False
        
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available - caching disabled")
            return
        
        try:
            if redis_url:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
            else:
                # Default to localhost
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=0,
                    decode_responses=True
                )
            
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            logger.info("Redis cache connected successfully")
        except (ConnectionError, TimeoutError, Exception) as e:
            logger.warning(f"Redis connection failed - caching disabled: {e}")
            self.enabled = False
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set a value in cache with optional TTL (seconds)."""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            if ttl:
                self.redis_client.setex(key, ttl, serialized)
            else:
                self.redis_client.set(key, serialized)
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    def delete(self, key: str):
        """Delete a key from cache."""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str):
        """Delete all keys matching a pattern."""
        if not self.enabled or not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error deleting cache pattern {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False
    
    def get_or_set(self, key: str, callable_func, ttl: Optional[int] = None) -> Any:
        """Get from cache or compute and set if not exists."""
        value = self.get(key)
        if value is not None:
            return value
        
        # Compute value
        value = callable_func()
        
        # Store in cache
        if value is not None:
            self.set(key, value, ttl)
        
        return value
    
    def invalidate_account(self, account_id: str):
        """Invalidate all cache entries for an account."""
        patterns = [
            f"account:{account_id}:*",
            f"positions:{account_id}:*",
            f"pnl:{account_id}:*",
            f"performance:{account_id}:*",
            f"trades:{account_id}:*",
        ]
        
        for pattern in patterns:
            self.delete_pattern(pattern)
    
    def invalidate_metrics(self, account_id: Optional[str] = None):
        """Invalidate metrics cache."""
        if account_id:
            self.delete_pattern(f"metrics:{account_id}:*")
        else:
            self.delete_pattern("metrics:*")


# Global cache manager instance
cache_manager = CacheManager()


def cache_key(*args, **kwargs) -> str:
    """Generate a cache key from arguments."""
    key_parts = []
    for arg in args:
        key_parts.append(str(arg))
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    
    key_string = ":".join(key_parts)
    # Hash if too long
    if len(key_string) > 200:
        key_string = hashlib.md5(key_string.encode()).hexdigest()
    
    return key_string


def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_str = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key_str)
            if cached_value is not None:
                return cached_value
            
            # Compute value
            result = await func(*args, **kwargs)
            
            # Store in cache
            if result is not None:
                cache_manager.set(cache_key_str, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_str = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key_str)
            if cached_value is not None:
                return cached_value
            
            # Compute value
            result = func(*args, **kwargs)
            
            # Store in cache
            if result is not None:
                cache_manager.set(cache_key_str, result, ttl)
            
            return result
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
