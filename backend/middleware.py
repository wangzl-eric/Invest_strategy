"""FastAPI middleware for request tracking and metrics."""
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.metrics import track_api_request

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to track API request metrics."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and track metrics."""
        start_time = time.time()
        
        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            status_code = 500
            response = Response(
                status_code=500,
                content=f"Internal Server Error: {str(e)}"
            )
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Track metrics
        try:
            track_api_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=status_code,
                duration=duration
            )
        except Exception as e:
            logger.warning(f"Error tracking metrics: {e}")
        
        return response
