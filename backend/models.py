"""SQLAlchemy database models."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class AccountSnapshot(Base):
    """Account snapshot at a point in time."""
    __tablename__ = "account_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Account values
    total_cash_value = Column(Float)
    net_liquidation = Column(Float)
    buying_power = Column(Float)
    gross_position_value = Column(Float)
    available_funds = Column(Float)
    excess_liquidity = Column(Float)
    
    # Calculated values
    equity = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Position(Base):
    """Current position snapshot."""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Contract details
    symbol = Column(String, nullable=False, index=True)
    sec_type = Column(String)  # STK, OPT, FUT, etc.
    currency = Column(String)
    exchange = Column(String)
    
    # Position details
    quantity = Column(Float, nullable=False)
    avg_cost = Column(Float)
    market_price = Column(Float)
    market_value = Column(Float)
    unrealized_pnl = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class PnLHistory(Base):
    """Historical PnL records."""
    __tablename__ = "pnl_history"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, nullable=False, index=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # PnL breakdown
    realized_pnl = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    mtm = Column(Float, default=0.0)  # Mark-to-Market PnL
    
    # Account values
    net_liquidation = Column(Float)
    total_cash = Column(Float)
    
    # Returns (calculated from net_liquidation)
    daily_return = Column(Float)  # Daily return: (net_liquidation_today / net_liquidation_yesterday) - 1
    cumulative_return = Column(Float)  # Cumulative return from start of series
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Trade(Base):
    """Trade execution record."""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, nullable=False, index=True)
    exec_id = Column(String, unique=True, nullable=False, index=True)
    exec_time = Column(DateTime, nullable=False, index=True)
    
    # Contract details
    symbol = Column(String, nullable=False, index=True)
    sec_type = Column(String)
    currency = Column(String)
    exchange = Column(String)
    
    # Execution details
    side = Column(String)  # BUY, SELL
    shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    avg_price = Column(Float)
    cum_qty = Column(Float)
    proceeds = Column(Float)
    
    # Commission and fees
    commission = Column(Float, default=0.0)
    taxes = Column(Float, default=0.0)
    
    # P&L
    cost_basis = Column(Float)
    realized_pnl = Column(Float, default=0.0)
    realized_pnl_base = Column(Float, default=0.0)  # P&L in base currency (HKD)
    mtm_pnl = Column(Float, default=0.0)
    
    # FX
    fx_rate_to_base = Column(Float, default=1.0)
    base_currency = Column(String, default="HKD")
    
    # Options specific
    underlying = Column(String)
    strike = Column(Float)
    expiry = Column(String)
    put_call = Column(String)
    multiplier = Column(Float, default=1.0)
    
    # Order info
    order_type = Column(String)
    trade_id = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class PerformanceMetric(Base):
    """Calculated performance metrics."""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, nullable=False, index=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Returns
    daily_return = Column(Float)
    cumulative_return = Column(Float)
    
    # Risk metrics
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    max_drawdown = Column(Float)
    
    # Trade statistics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float)
    avg_win = Column(Float)
    avg_loss = Column(Float)
    profit_factor = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class ExecutionOrder(Base):
    """Orders submitted by the strategy runner (paper or live)."""

    __tablename__ = "execution_orders"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    account_id = Column(String, index=True)
    mode = Column(String, nullable=False, default="paper")  # paper/live/sim

    symbol = Column(String, nullable=False, index=True)
    sec_type = Column(String, default="STK")
    currency = Column(String, default="USD")
    exchange = Column(String, default="")

    side = Column(String, nullable=False)  # BUY/SELL
    quantity = Column(Float, nullable=False)
    order_type = Column(String, default="MKT")  # MKT/LMT
    limit_price = Column(Float)

    status = Column(String, default="created")  # created/submitted/filled/cancelled/rejected
    external_order_id = Column(String, index=True)  # IBKR orderId or simulator id
    error = Column(Text, default="")


class ExecutionFill(Base):
    """Fills produced by the broker (paper or live)."""

    __tablename__ = "execution_fills"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    order_id = Column(Integer, ForeignKey("execution_orders.id"), index=True)
    symbol = Column(String, nullable=False, index=True)
    side = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    fill_price = Column(Float, nullable=False)
    commission = Column(Float, default=0.0)
    venue = Column(String, default="")
    exec_id = Column(String, index=True)


class RiskEvent(Base):
    """Risk engine events (blocks, warnings, kill-switch triggers)."""

    __tablename__ = "risk_events"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    severity = Column(String, default="WARN")  # INFO/WARN/ERROR
    event_type = Column(String, nullable=False)  # e.g. MAX_DAILY_LOSS, MAX_POSITION_NOTIONAL
    message = Column(Text, default="")
    context_json = Column(Text, default="{}")


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    accounts = relationship("UserAccount", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserAccount(Base):
    """Link between users and IBKR accounts."""
    __tablename__ = "user_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    account_id = Column(String, nullable=False, index=True)  # IBKR account ID
    account_name = Column(String)  # User-friendly name
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="accounts")


class UserPreferences(Base):
    """User preferences and settings."""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    default_account_id = Column(String)  # Default IBKR account to use
    theme = Column(String, default="dark")  # dark/light
    timezone = Column(String, default="UTC")
    currency = Column(String, default="USD")
    date_format = Column(String, default="YYYY-MM-DD")
    notifications_enabled = Column(Boolean, default=True)
    preferences_json = Column(Text, default="{}")  # Additional JSON preferences
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="preferences")


class APIKey(Base):
    """API keys for programmatic access."""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    key_name = Column(String, nullable=False)  # User-friendly name for the key
    key_hash = Column(String, unique=True, nullable=False, index=True)  # Hashed API key
    key_prefix = Column(String, nullable=False)  # First 8 chars for display
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)  # Optional expiration
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")


class Role(Base):
    """Role definitions for RBAC."""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)  # admin, viewer, trader, analyst
    description = Column(Text)
    permissions_json = Column(Text, default="{}")  # JSON object with permissions
    created_at = Column(DateTime, default=datetime.utcnow)


class UserRole(Base):
    """Many-to-many relationship between users and roles."""
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class AuditLog(Base):
    """Audit log for user actions."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    action = Column(String, nullable=False, index=True)  # login, logout, create, update, delete, etc.
    resource_type = Column(String, index=True)  # user, account, trade, etc.
    resource_id = Column(String, index=True)
    ip_address = Column(String)
    user_agent = Column(String)
    details_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class AlertRule(Base):
    """Configurable alert rules."""
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # Rule type: PNL_THRESHOLD, POSITION_SIZE, DRAWDOWN, VOLATILITY, CORRELATION
    rule_type = Column(String, nullable=False, index=True)
    
    # Rule configuration (JSON stored as text)
    # For PNL_THRESHOLD: {"threshold": -1000, "period": "daily"}
    # For POSITION_SIZE: {"symbol": "AAPL", "max_notional": 10000}
    # For DRAWDOWN: {"max_drawdown": 0.10}  # 10%
    # For VOLATILITY: {"max_volatility": 0.30}  # 30%
    # For CORRELATION: {"min_correlation": 0.7, "symbols": ["AAPL", "MSFT"]}
    rule_config = Column(Text, nullable=False)  # JSON string
    
    # Alert settings
    enabled = Column(Boolean, default=True, index=True)
    severity = Column(String, default="WARN")  # INFO/WARN/ERROR/CRITICAL
    
    # Notification channels (comma-separated channel IDs)
    channel_ids = Column(String, default="")
    
    # Cooldown period in minutes (prevent duplicate alerts)
    cooldown_minutes = Column(Integer, default=60)
    
    # Escalation
    escalation_enabled = Column(Boolean, default=False)
    escalation_after_minutes = Column(Integer, default=30)
    escalation_channel_ids = Column(String, default="")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Alert(Base):
    """Triggered alerts."""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("alert_rules.id"), nullable=False, index=True)
    account_id = Column(String, nullable=False, index=True)
    
    # Relationships
    rule = relationship("AlertRule", backref="alerts")
    
    # Alert details
    severity = Column(String, nullable=False, index=True)
    message = Column(Text, nullable=False)
    context_json = Column(Text, default="{}")  # Additional context data
    
    # Status
    status = Column(String, default="ACTIVE", index=True)  # ACTIVE, ACKNOWLEDGED, RESOLVED
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Notification tracking
    notifications_sent = Column(Boolean, default=False)
    notification_attempts = Column(Integer, default=0)
    last_notification_at = Column(DateTime, nullable=True)
    
    # Escalation
    escalated = Column(Boolean, default=False)
    escalated_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class AlertHistory(Base):
    """Historical record of alerts (for audit and analysis)."""
    __tablename__ = "alert_history"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False, index=True)
    rule_id = Column(Integer, ForeignKey("alert_rules.id"), nullable=False, index=True)
    account_id = Column(String, nullable=False, index=True)
    
    # Event details
    event_type = Column(String, nullable=False)  # TRIGGERED, ACKNOWLEDGED, RESOLVED, NOTIFICATION_SENT
    message = Column(Text)
    context_json = Column(Text, default="{}")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class AlertChannel(Base):
    """Notification channels for alerts."""
    __tablename__ = "alert_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    channel_type = Column(String, nullable=False, index=True)  # EMAIL, SMS, PUSH, SLACK, TEAMS, WEBHOOK
    
    # Channel configuration (JSON stored as text)
    # For EMAIL: {"to": "user@example.com", "smtp_server": "...", "smtp_port": 587, "username": "...", "password": "..."}
    # For SMS: {"phone_number": "+1234567890", "twilio_account_sid": "...", "twilio_auth_token": "...", "twilio_from": "..."}
    # For PUSH: {"endpoint": "...", "keys": {...}}
    # For SLACK: {"webhook_url": "..."}
    # For TEAMS: {"webhook_url": "..."}
    # For WEBHOOK: {"url": "...", "method": "POST", "headers": {...}}
    config_json = Column(Text, nullable=False)
    
    enabled = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

