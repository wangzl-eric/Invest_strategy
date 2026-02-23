"""Prometheus metrics collection for monitoring."""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from typing import Optional
import time

# API request metrics
api_requests_total = Counter(
    "api_requests_total",
    "Total number of API requests",
    ["method", "endpoint", "status"]
)

api_request_duration = Histogram(
    "api_request_duration_seconds",
    "API request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0)
)

# Data fetch metrics
data_fetch_total = Counter(
    "data_fetch_total",
    "Total number of data fetch operations",
    ["source", "status"]
)

data_fetch_duration = Histogram(
    "data_fetch_duration_seconds",
    "Data fetch duration in seconds",
    ["source"]
)

# Scheduler metrics
scheduler_runs_total = Counter(
    "scheduler_runs_total",
    "Total number of scheduler runs",
    ["job_name", "status"]
)

scheduler_last_run_time = Gauge(
    "scheduler_last_run_time_seconds",
    "Timestamp of last scheduler run",
    ["job_name"]
)

# IBKR connection metrics
ibkr_connection_status = Gauge(
    "ibkr_connection_status",
    "IBKR connection status (1=connected, 0=disconnected)",
)

ibkr_connection_errors_total = Counter(
    "ibkr_connection_errors_total",
    "Total number of IBKR connection errors"
)

# Database metrics
database_connection_status = Gauge(
    "database_connection_status",
    "Database connection status (1=connected, 0=disconnected)",
)

# Performance metrics
performance_calculation_duration = Histogram(
    "performance_calculation_duration_seconds",
    "Performance metrics calculation duration",
    ["metric_type"]
)


def track_api_request(method: str, endpoint: str, status_code: int, duration: float):
    """Track API request metrics."""
    status = f"{status_code // 100}xx"  # 2xx, 4xx, 5xx
    api_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    api_request_duration.labels(method=method, endpoint=endpoint).observe(duration)


def track_data_fetch(source: str, success: bool, duration: float):
    """Track data fetch metrics."""
    status = "success" if success else "error"
    data_fetch_total.labels(source=source, status=status).inc()
    data_fetch_duration.labels(source=source).observe(duration)


def track_scheduler_run(job_name: str, success: bool):
    """Track scheduler run metrics."""
    status = "success" if success else "error"
    scheduler_runs_total.labels(job_name=job_name, status=status).inc()
    scheduler_last_run_time.labels(job_name=job_name).set(time.time())


def set_ibkr_connection_status(connected: bool):
    """Update IBKR connection status."""
    ibkr_connection_status.set(1.0 if connected else 0.0)


def increment_ibkr_connection_errors():
    """Increment IBKR connection error counter."""
    ibkr_connection_errors_total.inc()


def set_database_connection_status(connected: bool):
    """Update database connection status."""
    database_connection_status.set(1.0 if connected else 0.0)


def track_performance_calculation(metric_type: str, duration: float):
    """Track performance calculation duration."""
    performance_calculation_duration.labels(metric_type=metric_type).observe(duration)


def get_metrics():
    """Get Prometheus metrics as string."""
    return generate_latest()


def get_metrics_content_type():
    """Get content type for metrics endpoint."""
    return CONTENT_TYPE_LATEST
