"""Error tracking and monitoring integration."""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import Sentry
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    HAS_SENTRY = True
except ImportError:
    HAS_SENTRY = False
    sentry_sdk = None


class ErrorTracker:
    """Error tracking service (Sentry integration)."""
    
    def __init__(self, dsn: Optional[str] = None, environment: str = "development"):
        self.dsn = dsn
        self.environment = environment
        self.initialized = False
        
        if HAS_SENTRY and dsn:
            try:
                sentry_sdk.init(
                    dsn=dsn,
                    environment=environment,
                    integrations=[
                        FastApiIntegration(),
                        SqlalchemyIntegration(),
                    ],
                    traces_sample_rate=0.1,  # 10% of transactions
                )
                self.initialized = True
                logger.info("Sentry error tracking initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Sentry: {e}")
        else:
            if not HAS_SENTRY:
                logger.warning("Sentry SDK not installed - error tracking disabled")
            elif not dsn:
                logger.info("Sentry DSN not configured - error tracking disabled")
    
    def capture_exception(self, exception: Exception, context: Optional[Dict[str, Any]] = None):
        """Capture an exception."""
        if self.initialized and HAS_SENTRY:
            with sentry_sdk.push_scope() as scope:
                if context:
                    for key, value in context.items():
                        scope.set_context(key, value)
                sentry_sdk.capture_exception(exception)
        else:
            # Fallback to logging
            logger.error(f"Exception: {exception}", exc_info=True, extra=context)
    
    def capture_message(self, message: str, level: str = "info", context: Optional[Dict[str, Any]] = None):
        """Capture a message."""
        if self.initialized and HAS_SENTRY:
            with sentry_sdk.push_scope() as scope:
                if context:
                    for key, value in context.items():
                        scope.set_context(key, value)
                sentry_sdk.capture_message(message, level=level)
        else:
            # Fallback to logging
            getattr(logger, level.lower())(message, extra=context)
    
    def set_user(self, user_id: Optional[str] = None, email: Optional[str] = None):
        """Set user context for error tracking."""
        if self.initialized and HAS_SENTRY:
            sentry_sdk.set_user({"id": user_id, "email": email})


# Global error tracker
error_tracker = ErrorTracker(
    dsn=None,  # Set via SENTRY_DSN environment variable
    environment="development"
)
