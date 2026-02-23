"""Rate limiting middleware for API protection."""
import time
import logging
from typing import Dict, Optional
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_windows: Dict[str, deque] = defaultdict(deque)
        self.hour_windows: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, identifier: str) -> tuple[bool, Optional[str]]:
        """
        Check if request is allowed.
        
        Returns: (is_allowed, error_message)
        """
        now = time.time()
        
        # Clean old entries (older than 1 minute)
        minute_window = self.minute_windows[identifier]
        while minute_window and now - minute_window[0] > 60:
            minute_window.popleft()
        
        # Clean old entries (older than 1 hour)
        hour_window = self.hour_windows[identifier]
        while hour_window and now - hour_window[0] > 3600:
            hour_window.popleft()
        
        # Check limits
        if len(minute_window) >= self.requests_per_minute:
            return False, f"Rate limit exceeded: {self.requests_per_minute} requests per minute"
        
        if len(hour_window) >= self.requests_per_hour:
            return False, f"Rate limit exceeded: {self.requests_per_hour} requests per hour"
        
        # Record request
        minute_window.append(now)
        hour_window.append(now)
        
        return True, None


# Global rate limiter
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    # Get client identifier (IP address or user ID)
    client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limit
    is_allowed, error_msg = rate_limiter.is_allowed(client_ip)
    
    if not is_allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": error_msg, "retry_after": 60}
        )
    
    response = await call_next(request)
    return response
