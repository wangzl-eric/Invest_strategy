# Alert System Setup Guide

## Overview

The alert system monitors your account data and sends notifications when configured conditions are met. This guide explains how to set it up and what triggers notifications.

## Setup Steps

### 1. Initialize Database

First, make sure the database tables are created:

```bash
conda run -n ibkr-analytics python scripts/init_db.py
```

This creates the following tables:
- `alert_rules` - Your alert configurations
- `alerts` - Triggered alerts
- `alert_history` - Audit trail
- `alert_channels` - Notification channels (email, SMS, etc.)

### 2. Create Notification Channels

Before creating alert rules, you need to set up at least one notification channel. Channels define **how** you receive alerts.

#### Example: Email Channel

```bash
curl -X POST "http://localhost:8000/api/alerts/channels" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "U1234567",
    "name": "My Email",
    "channel_type": "EMAIL",
    "config": {
      "to": "your-email@example.com",
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your-email@gmail.com",
      "password": "your-app-password",
      "from": "your-email@gmail.com"
    },
    "enabled": true
  }'
```

#### Example: Slack Channel

```bash
curl -X POST "http://localhost:8000/api/alerts/channels" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "U1234567",
    "name": "Slack Alerts",
    "channel_type": "SLACK",
    "config": {
      "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    },
    "enabled": true
  }'
```

#### Example: SMS Channel (Twilio)

```bash
curl -X POST "http://localhost:8000/api/alerts/channels" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "U1234567",
    "name": "SMS Alerts",
    "channel_type": "SMS",
    "config": {
      "phone_number": "+1234567890",
      "twilio_account_sid": "your-account-sid",
      "twilio_auth_token": "your-auth-token",
      "twilio_from": "+1234567890"
    },
    "enabled": true
  }'
```

#### Example: Webhook Channel

```bash
curl -X POST "http://localhost:8000/api/alerts/channels" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "U1234567",
    "name": "Custom Webhook",
    "channel_type": "WEBHOOK",
    "config": {
      "url": "https://your-server.com/webhook",
      "method": "POST",
      "headers": {
        "Authorization": "Bearer your-token"
      }
    },
    "enabled": true
  }'
```

**Note:** Save the channel `id` from the response - you'll need it when creating alert rules.

### 3. Create Alert Rules

Alert rules define **what** conditions trigger alerts. Each rule can use one or more notification channels.

#### Example: Daily Loss Limit

Alert when daily P&L drops below -$1000:

```bash
curl -X POST "http://localhost:8000/api/alerts/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "U1234567",
    "name": "Daily Loss Limit",
    "description": "Alert when daily loss exceeds $1000",
    "rule_type": "PNL_THRESHOLD",
    "rule_config": {
      "threshold": -1000,
      "period": "daily"
    },
    "severity": "ERROR",
    "channel_ids": [1],
    "cooldown_minutes": 60,
    "enabled": true
  }'
```

#### Example: Position Size Limit

Alert when any position exceeds $10,000 notional:

```bash
curl -X POST "http://localhost:8000/api/alerts/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "U1234567",
    "name": "Position Size Limit",
    "description": "Alert when position exceeds $10k",
    "rule_type": "POSITION_SIZE",
    "rule_config": {
      "symbol": null,
      "max_notional": 10000
    },
    "severity": "WARN",
    "channel_ids": [1],
    "cooldown_minutes": 30,
    "enabled": true
  }'
```

#### Example: Drawdown Alert

Alert when drawdown exceeds 10%:

```bash
curl -X POST "http://localhost:8000/api/alerts/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "U1234567",
    "name": "Max Drawdown",
    "description": "Alert when drawdown exceeds 10%",
    "rule_type": "DRAWDOWN",
    "rule_config": {
      "max_drawdown": 0.10
    },
    "severity": "WARN",
    "channel_ids": [1],
    "cooldown_minutes": 120,
    "enabled": true
  }'
```

#### Example: Volatility Alert

Alert when volatility exceeds 30%:

```bash
curl -X POST "http://localhost:8000/api/alerts/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "U1234567",
    "name": "High Volatility",
    "description": "Alert when volatility exceeds 30%",
    "rule_type": "VOLATILITY",
    "rule_config": {
      "max_volatility": 0.30,
      "lookback_days": 30
    },
    "severity": "WARN",
    "channel_ids": [1],
    "cooldown_minutes": 60,
    "enabled": true
  }'
```

### 4. Verify Setup

List your channels:
```bash
curl "http://localhost:8000/api/alerts/channels"
```

List your rules:
```bash
curl "http://localhost:8000/api/alerts/rules"
```

## What Triggers Notifications?

### Automatic Evaluation (Primary Method)

**The alert scheduler runs automatically every 1 minute** when the backend server is running. It:

1. Evaluates all enabled alert rules
2. Checks if conditions are met (P&L threshold, position size, drawdown, etc.)
3. Creates an alert if a condition is triggered
4. **Immediately sends notifications** via all configured channels
5. Respects cooldown periods to prevent duplicate alerts

**The scheduler starts automatically when you start the backend server** (see `backend/main.py`).

### Manual Evaluation

You can also manually trigger rule evaluation:

```bash
curl -X POST "http://localhost:8000/api/alerts/evaluate?account_id=U1234567"
```

This is useful for:
- Testing your rules
- Immediate evaluation after creating a new rule
- Debugging

### When Data Updates

The alert system evaluates rules:
- **Every 1 minute** (automatic scheduler)
- **After data updates** (if you have the data scheduler enabled)

## Alert Lifecycle

1. **Rule Evaluation**: Scheduler checks if rule condition is met
2. **Alert Creation**: If condition is met AND no active alert exists, create new alert
3. **Notification Sending**: Immediately send notifications via all configured channels
4. **Alert Status**: Alert starts as `ACTIVE`
5. **Acknowledgment**: You can acknowledge alerts via API
6. **Resolution**: You can resolve alerts when the condition is no longer met

## Rule Types

### PNL_THRESHOLD
- Monitors P&L against a threshold
- Config: `{"threshold": -1000, "period": "daily"}` (period: daily/weekly/monthly)

### POSITION_SIZE
- Monitors position sizes
- Config: `{"symbol": "AAPL", "max_notional": 10000}` (symbol: null for all positions)

### DRAWDOWN
- Monitors maximum drawdown
- Config: `{"max_drawdown": 0.10}` (0.10 = 10%)

### VOLATILITY
- Monitors portfolio volatility
- Config: `{"max_volatility": 0.30, "lookback_days": 30}` (0.30 = 30% annualized)

### CORRELATION
- Monitors correlation between positions (basic implementation)
- Config: `{"min_correlation": 0.7, "symbols": ["AAPL", "MSFT"]}`

## Cooldown Periods

Each rule has a `cooldown_minutes` setting that prevents duplicate alerts:
- If an alert is triggered, the rule won't trigger again until cooldown expires
- Example: `cooldown_minutes: 60` means max 1 alert per hour for that rule
- Cooldown is checked per rule, not per account

## Managing Alerts

### View Active Alerts
```bash
curl "http://localhost:8000/api/alerts?status=ACTIVE"
```

### Acknowledge an Alert
```bash
curl -X POST "http://localhost:8000/api/alerts/1/acknowledge?acknowledged_by=user@example.com"
```

### Resolve an Alert
```bash
curl -X POST "http://localhost:8000/api/alerts/1/resolve"
```

### View Alert History
```bash
curl "http://localhost:8000/api/alerts/1/history"
```

## Testing Your Setup

1. Create a test rule with a very low threshold (e.g., P&L threshold of $1,000,000)
2. Manually trigger evaluation: `POST /api/alerts/evaluate`
3. Check if alert was created: `GET /api/alerts`
4. Verify notification was sent (check email/Slack/etc.)
5. Delete or disable the test rule

## Troubleshooting

### Alerts Not Triggering
- Check if rules are enabled: `GET /api/alerts/rules`
- Check if channels are enabled: `GET /api/alerts/channels`
- Verify account has recent P&L data
- Check backend logs for errors

### Notifications Not Sending
- Verify channel configuration (test email/Slack webhook separately)
- Check backend logs for notification errors
- Ensure channel is enabled
- For email: Check SMTP credentials and firewall
- For SMS: Verify Twilio credentials and account balance

### Too Many Alerts
- Increase `cooldown_minutes` in your rules
- Adjust thresholds to be less sensitive
- Disable rules you don't need

## API Documentation

Full API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

All alert endpoints are under `/api/alerts/`:
- `/api/alerts/rules` - Manage alert rules
- `/api/alerts/channels` - Manage notification channels
- `/api/alerts` - View and manage alerts
- `/api/alerts/evaluate` - Manually trigger evaluation
