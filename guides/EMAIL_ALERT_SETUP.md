# Email Alert Setup Guide

## Step-by-Step: Setting Up Email Notifications

### Step 1: Prepare Your Email Credentials

You'll need SMTP settings for your email provider. Here are common providers:

#### Gmail
- **SMTP Server**: `smtp.gmail.com`
- **SMTP Port**: `587` (TLS) or `465` (SSL)
- **Username**: Your Gmail address
- **Password**: **App Password** (not your regular password)
  - Go to: https://myaccount.google.com/apppasswords
  - Generate an app password for "Mail"
  - Use that 16-character password

#### Outlook/Hotmail
- **SMTP Server**: `smtp-mail.outlook.com`
- **SMTP Port**: `587`
- **Username**: Your Outlook email
- **Password**: Your regular password

#### Yahoo Mail
- **SMTP Server**: `smtp.mail.yahoo.com`
- **SMTP Port**: `587`
- **Username**: Your Yahoo email
- **Password**: Your regular password (or app password)

#### Custom SMTP Server
- Ask your IT department or email provider for:
  - SMTP server address
  - SMTP port (usually 587 or 465)
  - Whether authentication is required

### Step 2: Start Your Backend Server

Make sure your backend is running:

```bash
conda run -n ibkr-analytics python backend/main.py
```

Or use the startup script:
```bash
./start.sh
```

The backend should be accessible at `http://localhost:8000`

### Step 3: Create Email Notification Channel

#### Option A: Using the API (curl)

```bash
curl -X POST "http://localhost:8000/api/alerts/channels" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "name": "My Email Alerts",
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

**Replace:**
- `YOUR_ACCOUNT_ID` with your IBKR account ID (e.g., "U1234567")
- `your-email@example.com` with the email address where you want to receive alerts
- `smtp.gmail.com` with your email provider's SMTP server
- `587` with the correct port for your provider
- `your-email@gmail.com` with your email address
- `your-app-password` with your email password or app password

#### Option B: Using Swagger UI (Easier)

1. Open your browser and go to: `http://localhost:8000/docs`
2. Find the section **"alerts"** → **POST /api/alerts/channels**
3. Click "Try it out"
4. Fill in the request body:

```json
{
  "account_id": "YOUR_ACCOUNT_ID",
  "name": "My Email Alerts",
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
}
```

5. Click "Execute"
6. **Save the `id` from the response** - you'll need it in the next step!

Example response:
```json
{
  "id": 1,
  "account_id": "U1234567",
  "name": "My Email Alerts",
  ...
}
```

### Step 4: Create an Alert Rule

Now create a rule that will trigger email alerts. Here's a simple example for daily loss alerts:

#### Option A: Using the API (curl)

```bash
curl -X POST "http://localhost:8000/api/alerts/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "name": "Daily Loss Alert",
    "description": "Email me when daily loss exceeds $500",
    "rule_type": "PNL_THRESHOLD",
    "rule_config": {
      "threshold": -500,
      "period": "daily"
    },
    "severity": "ERROR",
    "channel_ids": [1],
    "cooldown_minutes": 60,
    "enabled": true
  }'
```

**Replace:**
- `YOUR_ACCOUNT_ID` with your IBKR account ID
- `[1]` with the channel ID from Step 3 (the `id` you saved)
- `-500` with your desired loss threshold (negative number = loss)

#### Option B: Using Swagger UI

1. In Swagger UI, find **POST /api/alerts/rules**
2. Click "Try it out"
3. Fill in the request body:

```json
{
  "account_id": "YOUR_ACCOUNT_ID",
  "name": "Daily Loss Alert",
  "description": "Email me when daily loss exceeds $500",
  "rule_type": "PNL_THRESHOLD",
  "rule_config": {
    "threshold": -500,
    "period": "daily"
  },
  "severity": "ERROR",
  "channel_ids": [1],
  "cooldown_minutes": 60,
  "enabled": true
}
```

4. Click "Execute"

### Step 5: Test Your Setup

#### Test 1: Verify Channel Created

```bash
curl "http://localhost:8000/api/alerts/channels"
```

You should see your email channel in the list.

#### Test 2: Verify Rule Created

```bash
curl "http://localhost:8000/api/alerts/rules"
```

You should see your alert rule in the list.

#### Test 3: Manually Trigger Evaluation

To test if emails are sent, manually trigger rule evaluation:

```bash
curl -X POST "http://localhost:8000/api/alerts/evaluate?account_id=YOUR_ACCOUNT_ID"
```

**Note:** This will only send an email if the rule condition is actually met (e.g., if your daily P&L is below -$500).

#### Test 4: Create a Test Rule (Recommended)

Create a test rule with a very high threshold that will definitely trigger:

```bash
curl -X POST "http://localhost:8000/api/alerts/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "name": "TEST - Always Trigger",
    "rule_type": "PNL_THRESHOLD",
    "rule_config": {
      "threshold": 999999999,
      "period": "daily"
    },
    "severity": "INFO",
    "channel_ids": [1],
    "cooldown_minutes": 1,
    "enabled": true
  }'
```

Then trigger evaluation:
```bash
curl -X POST "http://localhost:8000/api/alerts/evaluate?account_id=YOUR_ACCOUNT_ID"
```

Check your email! You should receive an alert.

**Remember to delete the test rule after testing:**
```bash
curl -X DELETE "http://localhost:8000/api/alerts/rules/TEST_RULE_ID"
```

### Step 6: Verify Automatic Alerts

The alert system automatically evaluates rules **every 1 minute** when the backend is running. 

To verify:
1. Make sure your backend is running
2. Wait for a condition to be met (or create a test rule)
3. Check your email inbox
4. Check the alerts API: `GET /api/alerts` to see triggered alerts

## Common Alert Rule Examples

### Daily Loss Limit
```json
{
  "account_id": "YOUR_ACCOUNT_ID",
  "name": "Daily Loss Limit",
  "rule_type": "PNL_THRESHOLD",
  "rule_config": {
    "threshold": -1000,
    "period": "daily"
  },
  "severity": "ERROR",
  "channel_ids": [1],
  "cooldown_minutes": 60
}
```

### Position Size Alert
```json
{
  "account_id": "YOUR_ACCOUNT_ID",
  "name": "Large Position Alert",
  "rule_type": "POSITION_SIZE",
  "rule_config": {
    "symbol": null,
    "max_notional": 50000
  },
  "severity": "WARN",
  "channel_ids": [1],
  "cooldown_minutes": 30
}
```

### Drawdown Alert
```json
{
  "account_id": "YOUR_ACCOUNT_ID",
  "name": "Max Drawdown",
  "rule_type": "DRAWDOWN",
  "rule_config": {
    "max_drawdown": 0.10
  },
  "severity": "WARN",
  "channel_ids": [1],
  "cooldown_minutes": 120
}
```

## Troubleshooting

### No Email Received

1. **Check backend logs** for errors:
   ```bash
   tail -f backend.log
   ```

2. **Verify SMTP settings:**
   - Double-check SMTP server and port
   - For Gmail, make sure you're using an App Password, not your regular password
   - Test SMTP connection manually if possible

3. **Check spam folder** - emails might be filtered

4. **Verify channel is enabled:**
   ```bash
   curl "http://localhost:8000/api/alerts/channels"
   ```
   Make sure `"enabled": true`

5. **Check if alert was created:**
   ```bash
   curl "http://localhost:8000/api/alerts"
   ```
   If you see an alert but no email, the issue is with email configuration.

### SMTP Authentication Error

- **Gmail**: Use App Password, not regular password
- **2FA enabled**: Most providers require app-specific passwords
- **Wrong port**: Try 587 (TLS) or 465 (SSL)
- **Firewall**: Make sure port 587/465 is not blocked

### "Connection Refused" Error

- Check if SMTP server address is correct
- Verify port number
- Check firewall settings
- Some networks block SMTP - try from different network

### Test Email Connection Manually

You can test your SMTP settings with Python:

```python
import smtplib
from email.mime.text import MIMEText

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your-email@gmail.com', 'your-app-password')
    
    msg = MIMEText('Test email')
    msg['Subject'] = 'Test'
    msg['From'] = 'your-email@gmail.com'
    msg['To'] = 'your-email@gmail.com'
    
    server.send_message(msg)
    server.quit()
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
```

## Viewing Your Alerts

### List All Alerts
```bash
curl "http://localhost:8000/api/alerts"
```

### List Active Alerts Only
```bash
curl "http://localhost:8000/api/alerts?status=ACTIVE"
```

### View Alert Details
```bash
curl "http://localhost:8000/api/alerts/ALERT_ID"
```

## Managing Your Email Channel

### Update Email Settings
```bash
curl -X PUT "http://localhost:8000/api/alerts/channels/1" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "to": "new-email@example.com",
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your-email@gmail.com",
      "password": "your-app-password"
    }
  }'
```

### Disable Email Channel (Temporarily)
```bash
curl -X PUT "http://localhost:8000/api/alerts/channels/1" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

### Delete Email Channel
```bash
curl -X DELETE "http://localhost:8000/api/alerts/channels/1"
```

## Next Steps

Once email alerts are working:
1. Create more alert rules for different conditions
2. Set up multiple channels (Slack, SMS, etc.)
3. Adjust cooldown periods to avoid email spam
4. Monitor alerts via the API or dashboard

For more information, see:
- Full alert setup guide: `docs/ALERT_SETUP_GUIDE.md`
- API documentation: `http://localhost:8000/docs`
