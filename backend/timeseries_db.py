"""Time-series database integration for efficient time-range queries."""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

# Try to import TimescaleDB/PostgreSQL extensions
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.dialects.postgresql import insert
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

# Try to import InfluxDB
try:
    from influxdb_client import InfluxDBClient, Point
    from influxdb_client.client.write_api import SYNCHRONOUS
    HAS_INFLUXDB = True
except ImportError:
    HAS_INFLUXDB = False


class TimeSeriesDB:
    """Time-series database abstraction layer."""
    
    def __init__(self, db_type: str = "timescaledb", connection_string: Optional[str] = None):
        """
        Initialize time-series database.
        
        Args:
            db_type: "timescaledb", "influxdb", or "postgresql"
            connection_string: Database connection string
        """
        self.db_type = db_type
        self.connection_string = connection_string
        self.client = None
        self.engine = None
        
        if db_type == "timescaledb" or db_type == "postgresql":
            if not HAS_POSTGRES:
                logger.warning("PostgreSQL/TimescaleDB not available")
                return
            
            if connection_string:
                self.engine = create_engine(connection_string)
            else:
                # Use default from settings
                from backend.config import settings
                db_url = settings.database.url
                if db_url.startswith("sqlite"):
                    logger.warning("SQLite does not support TimescaleDB. Use PostgreSQL.")
                    return
                self.engine = create_engine(db_url)
            
            # Check if TimescaleDB extension is available
            try:
                with self.engine.connect() as conn:
                    result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'timescaledb'"))
                    if result.fetchone():
                        logger.info("TimescaleDB extension detected")
                    else:
                        logger.info("Using standard PostgreSQL (TimescaleDB extension not installed)")
            except Exception as e:
                logger.warning(f"Could not check TimescaleDB extension: {e}")
        
        elif db_type == "influxdb":
            if not HAS_INFLUXDB:
                logger.warning("InfluxDB client not available")
                return
            
            # Parse connection string: influxdb://token@host:port/org/bucket
            if connection_string:
                # Parse URL
                import urllib.parse
                parsed = urllib.parse.urlparse(connection_string)
                token = parsed.username
                host = parsed.hostname
                port = parsed.port or 8086
                org = parsed.path.split('/')[1] if len(parsed.path.split('/')) > 1 else "my-org"
                bucket = parsed.path.split('/')[2] if len(parsed.path.split('/')) > 2 else "my-bucket"
                
                self.client = InfluxDBClient(
                    url=f"http://{host}:{port}",
                    token=token,
                    org=org
                )
                self.bucket = bucket
                self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
                logger.info(f"InfluxDB connected: {host}:{port}/{org}/{bucket}")
    
    def create_hypertable(self, table_name: str, time_column: str = "timestamp"):
        """Create a TimescaleDB hypertable for time-series optimization."""
        if self.db_type not in ["timescaledb", "postgresql"] or not self.engine:
            logger.warning("Cannot create hypertable: not using PostgreSQL/TimescaleDB")
            return False
        
        try:
            with self.engine.connect() as conn:
                # Check if hypertable already exists
                check_sql = text("""
                    SELECT * FROM timescaledb_information.hypertables 
                    WHERE hypertable_name = :table_name
                """)
                result = conn.execute(check_sql, {"table_name": table_name})
                if result.fetchone():
                    logger.info(f"Hypertable {table_name} already exists")
                    return True
                
                # Create hypertable
                create_sql = text(f"""
                    SELECT create_hypertable('{table_name}', '{time_column}',
                        if_not_exists => TRUE,
                        chunk_time_interval => INTERVAL '1 day'
                    )
                """)
                conn.execute(create_sql)
                conn.commit()
                logger.info(f"Created hypertable {table_name}")
                return True
        except Exception as e:
            logger.error(f"Error creating hypertable: {e}")
            return False
    
    def write_time_series(
        self,
        measurement: str,
        tags: Dict[str, str],
        fields: Dict[str, float],
        timestamp: datetime
    ):
        """Write a time-series data point."""
        if self.db_type == "influxdb" and self.client:
            point = Point(measurement)
            for key, value in tags.items():
                point = point.tag(key, value)
            for key, value in fields.items():
                point = point.field(key, value)
            point = point.time(timestamp)
            
            self.write_api.write(bucket=self.bucket, record=point)
            return True
        else:
            logger.warning("Time-series write not implemented for this database type")
            return False
    
    def query_time_series(
        self,
        measurement: str,
        tags: Optional[Dict[str, str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """Query time-series data."""
        if self.db_type == "influxdb" and self.client:
            query = f'from(bucket: "{self.bucket}") |> range(start: {start_time.isoformat() if start_time else "-30d"}, stop: {end_time.isoformat() if end_time else "now()"})'
            query += f' |> filter(fn: (r) => r["_measurement"] == "{measurement}")'
            
            if tags:
                for key, value in tags.items():
                    query += f' |> filter(fn: (r) => r["{key}"] == "{value}")'
            
            if limit:
                query += f' |> limit(n: {limit})'
            
            query_api = self.client.query_api()
            result = query_api.query_data_frame(query)
            
            if isinstance(result, list):
                if result:
                    return pd.concat(result)
                return pd.DataFrame()
            return result if isinstance(result, pd.DataFrame) else pd.DataFrame()
        
        else:
            logger.warning("Time-series query not implemented for this database type")
            return pd.DataFrame()
    
    def optimize_for_time_series(self, table_name: str):
        """Optimize a table for time-series queries (add indexes, etc.)."""
        if self.db_type not in ["timescaledb", "postgresql"] or not self.engine:
            return False
        
        try:
            with self.engine.connect() as conn:
                # Create index on timestamp if it doesn't exist
                index_sql = text(f"""
                    CREATE INDEX IF NOT EXISTS idx_{table_name}_timestamp 
                    ON {table_name} (timestamp DESC)
                """)
                conn.execute(index_sql)
                conn.commit()
                logger.info(f"Optimized table {table_name} for time-series queries")
                return True
        except Exception as e:
            logger.error(f"Error optimizing table: {e}")
            return False


# Global time-series DB instance (lazy initialization)
_timeseries_db: Optional[TimeSeriesDB] = None


def get_timeseries_db() -> Optional[TimeSeriesDB]:
    """Get or create the global time-series DB instance."""
    global _timeseries_db
    
    if _timeseries_db is None:
        # Try to initialize from config
        from backend.config import settings
        db_url = settings.database.url
        
        if db_url.startswith("postgresql"):
            _timeseries_db = TimeSeriesDB("timescaledb", db_url)
        else:
            logger.warning("Time-series DB not configured (requires PostgreSQL/TimescaleDB or InfluxDB)")
    
    return _timeseries_db
