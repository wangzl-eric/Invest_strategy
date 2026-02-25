"""FastAPI application entry point."""
import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.api.backtest_routes import router as backtest_router
from backend.api.auth_routes import router as auth_router
from backend.api.advanced_analytics_routes import router as advanced_analytics_router
from backend.api.advanced_analytics_routes_extended import router as advanced_analytics_extended_router
from backend.api.alert_routes import router as alert_router
from backend.api.reporting_routes import router as reporting_router
from backend.api.market_routes import router as market_router
from backend.api.data_routes import router as data_router
from backend.api.execution_routes import router as execution_router
from backend.broker_interface import broker_manager, IBKRBrokerAdapter
from backend.ibkr_client import IBKRClient
try:
    from backend.api.websocket_routes import router as websocket_router
except ImportError:
    websocket_router = None
from backend.config import settings
from backend.scheduler import PnLScheduler
from backend.middleware import MetricsMiddleware
from backend.rate_limiter import rate_limit_middleware
from backend.error_tracking import error_tracker
from backend.tracing import tracing_service
from backend.realtime_broadcaster import broadcaster
from backend.alert_engine import alert_engine

# Configure logging
import os
try:
    from backend.logging_config import setup_logging
    use_json_logging = os.getenv("LOG_FORMAT", "").lower() == "json"
    setup_logging(
        log_level=settings.app.log_level,
        use_json=use_json_logging
    )
except ImportError:
    logging.basicConfig(
        level=getattr(logging, settings.app.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="IBKR Analytics API",
    description="API for analyzing IBKR account PnL, positions, and performance",
    version="1.0.0",
    debug=settings.app.debug,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics middleware
app.add_middleware(MetricsMiddleware)

# Rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Initialize error tracking
import os
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    error_tracker.dsn = sentry_dsn
    error_tracker.environment = os.getenv("ENVIRONMENT", "production")
    error_tracker.__init__(sentry_dsn, error_tracker.environment)

# Initialize distributed tracing
tracing_enabled = os.getenv("TRACING_ENABLED", "false").lower() == "true"
otlp_endpoint = os.getenv("OTLP_ENDPOINT")
if tracing_enabled:
    tracing_service.enabled = True
    tracing_service.otlp_endpoint = otlp_endpoint
    tracing_service.__init__(True, otlp_endpoint)
    tracing_service.instrument_fastapi(app)
    tracing_service.instrument_sqlalchemy()

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(router, prefix="/api", tags=["api"])
app.include_router(backtest_router, prefix="/api", tags=["backtest"])
app.include_router(advanced_analytics_router, prefix="/api/analytics", tags=["advanced-analytics"])
app.include_router(advanced_analytics_extended_router, prefix="/api/analytics", tags=["advanced-analytics"])
app.include_router(alert_router, prefix="/api", tags=["alerts"])
app.include_router(reporting_router, prefix="/api", tags=["reporting"])
app.include_router(market_router, prefix="/api", tags=["market-data"])
app.include_router(data_router, prefix="/api", tags=["data-management"])
app.include_router(execution_router, prefix="/api", tags=["execution"])
if websocket_router:
    app.include_router(websocket_router, prefix="/api", tags=["websocket"])

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from backend.metrics import get_metrics, get_metrics_content_type
    from fastapi import Response
    return Response(content=get_metrics(), media_type=get_metrics_content_type())

# NOTE: PnL scheduler disabled.
# The user explicitly does not want ongoing PnL recording anymore.
# We keep the class import available for optional/legacy usage, but do not start it automatically.
pnl_scheduler = None


@app.on_event("startup")
async def startup_event():
    """Application startup hook."""
    logger.info("PnL scheduler disabled (no automatic PnL recording)")
    # Start real-time broadcaster
    await broadcaster.start()
    logger.info("Real-time broadcaster started")
    # Start alert evaluation scheduler
    try:
        from backend.alert_scheduler import start_alert_scheduler
        start_alert_scheduler()
        logger.info("Alert scheduler started")
    except Exception as e:
        logger.warning(f"Failed to start alert scheduler: {e}")
    # Register IBKR broker
    try:
        ibkr_client = IBKRClient()
        ibkr_adapter = IBKRBrokerAdapter(ibkr_client)
        broker_manager.register_broker("ibkr", ibkr_adapter)
        logger.info("IBKR broker registered")
    except Exception as e:
        logger.warning(f"Failed to register IBKR broker: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown hook."""
    # No-op: scheduler disabled
    logger.info("PnL scheduler disabled (nothing to stop)")
    # Stop real-time broadcaster
    await broadcaster.stop()
    logger.info("Real-time broadcaster stopped")
    # Stop alert scheduler
    try:
        from backend.alert_scheduler import stop_alert_scheduler
        stop_alert_scheduler()
        logger.info("Alert scheduler stopped")
    except Exception as e:
        logger.warning(f"Error stopping alert scheduler: {e}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "IBKR Analytics API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/health")
async def api_health_check():
    """API health check endpoint."""
    return {"status": "healthy", "service": "api"}


@app.get("/api/health/ibkr")
async def ibkr_status_check():
    """IBKR reachability check + data freshness report."""
    import socket
    from sqlalchemy import desc, func
    from backend.database import engine
    from backend.models import AccountSnapshot, Position, PnLHistory

    host = settings.ibkr.host
    port = settings.ibkr.port
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        reachable = result == 0
    except Exception:
        reachable = False

    # Data freshness — latest timestamps per table
    freshness = {}
    try:
        from sqlalchemy.orm import Session
        with Session(engine) as db:
            for label, model, ts_col in [
                ("positions", Position, Position.timestamp),
                ("account", AccountSnapshot, AccountSnapshot.timestamp),
                ("pnl", PnLHistory, PnLHistory.date),
            ]:
                row = db.query(func.max(ts_col)).scalar()
                if row:
                    age_seconds = (datetime.utcnow() - row).total_seconds()
                    freshness[label] = {
                        "latest": row.isoformat(),
                        "age_seconds": round(age_seconds, 1),
                        "stale": age_seconds > 3600,
                    }
                else:
                    freshness[label] = {"latest": None, "age_seconds": None, "stale": True}
    except Exception as e:
        freshness["error"] = str(e)

    any_stale = any(v.get("stale", True) for v in freshness.values() if isinstance(v, dict))

    return {
        "ibkr_reachable": reachable,
        "host": host,
        "port": port,
        "message": "TWS/Gateway is running" if reachable else "TWS/Gateway is NOT reachable — please start it",
        "data_freshness": freshness,
        "any_stale": any_stale,
    }


@app.get("/api/health/detailed")
async def detailed_health_check():
    """Detailed health check with component-level status."""
    from backend.database import engine
    from backend.config import settings
    from backend.ibkr_client import IBKRClient
    from backend.scheduler import PnLScheduler
    import socket
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }
    
    # Database health
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["components"]["database"] = {
            "status": "healthy",
            "url": settings.database.url.split("@")[-1] if "@" in settings.database.url else "sqlite"
        }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # IBKR connection health
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((settings.ibkr.host, settings.ibkr.port))
        sock.close()
        
        if result == 0:
            # Port is open, try actual connection
            ibkr_client = IBKRClient()
            connected = await ibkr_client.connect()
            await ibkr_client.disconnect()
            
            health_status["components"]["ibkr"] = {
                "status": "healthy" if connected else "unhealthy",
                "host": settings.ibkr.host,
                "port": settings.ibkr.port,
                "connected": connected
            }
            if not connected:
                health_status["status"] = "degraded"
        else:
            health_status["components"]["ibkr"] = {
                "status": "unhealthy",
                "host": settings.ibkr.host,
                "port": settings.ibkr.port,
                "error": "Port not accessible"
            }
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["ibkr"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Scheduler health
    # The periodic PnL recording scheduler is intentionally disabled.
    health_status["components"]["scheduler"] = {
        "status": "disabled",
        "reason": "Automatic PnL recording disabled by user request"
    }
    
    # Cache health
    try:
        from backend.cache import cache_manager
        health_status["components"]["cache"] = {
            "status": "healthy" if cache_manager.enabled else "disabled",
            "enabled": cache_manager.enabled
        }
    except Exception as e:
        health_status["components"]["cache"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Alert system health
    try:
        from backend.alert_scheduler import scheduler as alert_scheduler
        health_status["components"]["alerts"] = {
            "status": "healthy" if alert_scheduler.running else "stopped",
            "running": alert_scheduler.running if hasattr(alert_scheduler, 'running') else False
        }
    except Exception as e:
        health_status["components"]["alerts"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.app.debug,
    )

