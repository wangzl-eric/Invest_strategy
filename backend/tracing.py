"""Distributed tracing with OpenTelemetry."""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import OpenTelemetry
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    HAS_OPENTELEMETRY = True
except ImportError:
    HAS_OPENTELEMETRY = False
    trace = None


class TracingService:
    """Distributed tracing service."""
    
    def __init__(self, enabled: bool = False, otlp_endpoint: Optional[str] = None):
        self.enabled = enabled
        self.otlp_endpoint = otlp_endpoint
        self.tracer = None
        
        if enabled and HAS_OPENTELEMETRY:
            try:
                # Setup tracer provider
                provider = TracerProvider()
                trace.set_tracer_provider(provider)
                
                # Add span processor
                if otlp_endpoint:
                    # Export to OTLP collector
                    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
                    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
                else:
                    # Console exporter for development
                    console_exporter = ConsoleSpanExporter()
                    provider.add_span_processor(BatchSpanProcessor(console_exporter))
                
                self.tracer = trace.get_tracer(__name__)
                logger.info("OpenTelemetry tracing initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenTelemetry: {e}")
        elif enabled and not HAS_OPENTELEMETRY:
            logger.warning("OpenTelemetry not installed - tracing disabled")
    
    def get_tracer(self):
        """Get the tracer instance."""
        return self.tracer
    
    def instrument_fastapi(self, app):
        """Instrument FastAPI app for automatic tracing."""
        if self.enabled and HAS_OPENTELEMETRY:
            try:
                FastAPIInstrumentor.instrument_app(app)
                logger.info("FastAPI instrumented for tracing")
            except Exception as e:
                logger.warning(f"Failed to instrument FastAPI: {e}")
    
    def instrument_sqlalchemy(self):
        """Instrument SQLAlchemy for database query tracing."""
        if self.enabled and HAS_OPENTELEMETRY:
            try:
                SQLAlchemyInstrumentor().instrument()
                logger.info("SQLAlchemy instrumented for tracing")
            except Exception as e:
                logger.warning(f"Failed to instrument SQLAlchemy: {e}")


# Global tracing service
tracing_service = TracingService(
    enabled=False,  # Enable via TRACING_ENABLED environment variable
    otlp_endpoint=None  # Set via OTLP_ENDPOINT environment variable
)
