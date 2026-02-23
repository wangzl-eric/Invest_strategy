"""Notification service for sending alerts via multiple channels."""
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import aiohttp

from backend.models import AlertChannel, Alert, AlertRule

logger = logging.getLogger(__name__)


class NotificationService:
    """Handles sending notifications via various channels."""
    
    async def send_notification(self, channel: AlertChannel, alert: Alert, rule: AlertRule):
        """Send a notification via the specified channel."""
        try:
            config = json.loads(channel.config_json)
            
            if channel.channel_type == "EMAIL":
                # Run email in thread pool since it's synchronous
                import asyncio
                await asyncio.get_event_loop().run_in_executor(
                    None, self._send_email, channel, alert, rule, config
                )
            elif channel.channel_type == "SMS":
                await self._send_sms(channel, alert, rule, config)
            elif channel.channel_type == "SLACK":
                await self._send_slack(channel, alert, rule, config)
            elif channel.channel_type == "TEAMS":
                await self._send_teams(channel, alert, rule, config)
            elif channel.channel_type == "WEBHOOK":
                await self._send_webhook(channel, alert, rule, config)
            elif channel.channel_type == "PUSH":
                await self._send_push(channel, alert, rule, config)
            else:
                logger.warning(f"Unknown channel type: {channel.channel_type}")
        except Exception as e:
            logger.error(f"Error sending notification via {channel.channel_type}: {e}", exc_info=True)
            raise
    
    def _send_email(self, channel: AlertChannel, alert: Alert, rule: AlertRule, config: dict):
        """Send email notification."""
        to_email = config.get("to")
        smtp_server = config.get("smtp_server", "smtp.gmail.com")
        smtp_port = config.get("smtp_port", 587)
        username = config.get("username")
        password = config.get("password")
        from_email = config.get("from", username)
        
        if not to_email:
            raise ValueError("Email 'to' address not configured")
        
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = f"Alert: {rule.name} - {alert.severity}"
        
        body = f"""
        Alert: {rule.name}
        Account: {alert.account_id}
        Severity: {alert.severity}
        Message: {alert.message}
        
        Rule: {rule.description or rule.name}
        Time: {alert.created_at}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            if username and password:
                server.login(username, password)
            server.send_message(msg)
            server.quit()
            logger.info(f"Email sent to {to_email}")
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise
    
    async def _send_sms(self, channel: AlertChannel, alert: Alert, rule: AlertRule, config: dict):
        """Send SMS via Twilio."""
        phone_number = config.get("phone_number")
        account_sid = config.get("twilio_account_sid")
        auth_token = config.get("twilio_auth_token")
        from_number = config.get("twilio_from")
        
        if not all([phone_number, account_sid, auth_token, from_number]):
            raise ValueError("Twilio configuration incomplete")
        
        try:
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            
            message = f"Alert: {rule.name}\n{alert.message}\nAccount: {alert.account_id}"
            
            client.messages.create(
                body=message,
                from_=from_number,
                to=phone_number
            )
            logger.info(f"SMS sent to {phone_number}")
        except ImportError:
            logger.error("Twilio library not installed")
            raise
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            raise
    
    async def _send_slack(self, channel: AlertChannel, alert: Alert, rule: AlertRule, config: dict):
        """Send Slack webhook notification."""
        webhook_url = config.get("webhook_url")
        
        if not webhook_url:
            raise ValueError("Slack webhook URL not configured")
        
        payload = {
            "text": f"Alert: {rule.name}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"Alert: {rule.name}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Severity:*\n{alert.severity}"},
                        {"type": "mrkdwn", "text": f"*Account:*\n{alert.account_id}"},
                        {"type": "mrkdwn", "text": f"*Message:*\n{alert.message}"},
                        {"type": "mrkdwn", "text": f"*Time:*\n{alert.created_at}"}
                    ]
                }
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"Slack webhook returned {response.status}")
                logger.info("Slack notification sent")
    
    async def _send_teams(self, channel: AlertChannel, alert: Alert, rule: AlertRule, config: dict):
        """Send Microsoft Teams webhook notification."""
        webhook_url = config.get("webhook_url")
        
        if not webhook_url:
            raise ValueError("Teams webhook URL not configured")
        
        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": f"Alert: {rule.name}",
            "themeColor": "FF0000" if alert.severity in ["ERROR", "CRITICAL"] else "FFA500",
            "title": f"Alert: {rule.name}",
            "sections": [
                {
                    "activityTitle": rule.name,
                    "facts": [
                        {"name": "Severity", "value": alert.severity},
                        {"name": "Account", "value": alert.account_id},
                        {"name": "Message", "value": alert.message},
                        {"name": "Time", "value": str(alert.created_at)}
                    ]
                }
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"Teams webhook returned {response.status}")
                logger.info("Teams notification sent")
    
    async def _send_webhook(self, channel: AlertChannel, alert: Alert, rule: AlertRule, config: dict):
        """Send generic webhook notification."""
        url = config.get("url")
        method = config.get("method", "POST")
        headers = config.get("headers", {})
        
        if not url:
            raise ValueError("Webhook URL not configured")
        
        payload = {
            "alert_id": alert.id,
            "rule_name": rule.name,
            "account_id": alert.account_id,
            "severity": alert.severity,
            "message": alert.message,
            "created_at": alert.created_at.isoformat(),
            "context": json.loads(alert.context_json) if alert.context_json else {}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, json=payload, headers=headers) as response:
                if response.status not in [200, 201, 204]:
                    raise Exception(f"Webhook returned {response.status}")
                logger.info(f"Webhook notification sent to {url}")
    
    async def _send_push(self, channel: AlertChannel, alert: Alert, rule: AlertRule, config: dict):
        """Send push notification (web push)."""
        # This would require web push library and service worker setup
        # For now, just log
        logger.info(f"Push notification would be sent for alert {alert.id}")
        # TODO: Implement web push notifications


# Global notification service
notification_service = NotificationService()
