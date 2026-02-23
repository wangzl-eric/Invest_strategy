"""Alert engine for monitoring and triggering alerts based on configurable rules."""
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, inspect
from sqlalchemy.exc import OperationalError

from backend.database import get_db_context
from backend.models import AlertRule, Alert, AlertHistory, AlertChannel, PnLHistory, Position, AccountSnapshot
from backend.notifications import NotificationService

logger = logging.getLogger(__name__)


class AlertEngine:
    """Evaluates alert rules and triggers notifications."""
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.last_evaluation: Dict[int, datetime] = {}  # Track last evaluation per rule
    
    def evaluate_all_rules(self, account_id: Optional[str] = None):
        """Evaluate all enabled alert rules."""
        try:
            with get_db_context() as db:
                # Check if alert_rules table exists
                try:
                    inspector = inspect(db.bind)
                    table_names = inspector.get_table_names()
                    if 'alert_rules' not in table_names:
                        logger.debug("alert_rules table does not exist, skipping alert evaluation")
                        return
                except Exception:
                    # If inspection fails, try querying directly and catch OperationalError
                    pass
                
                query = db.query(AlertRule).filter(AlertRule.enabled == True)
                
                if account_id:
                    query = query.filter(AlertRule.account_id == account_id)
                
                rules = query.all()
                
                for rule in rules:
                    try:
                        self.evaluate_rule(rule, db)
                    except Exception as e:
                        logger.error(f"Error evaluating rule {rule.id}: {e}", exc_info=True)
        except OperationalError as e:
            # Handle case where table doesn't exist
            if 'no such table: alert_rules' in str(e).lower():
                logger.debug("alert_rules table does not exist, skipping alert evaluation")
            else:
                logger.warning(f"Database error in alert evaluation: {e}")
        except Exception as e:
            # Handle other errors gracefully
            logger.debug(f"Alert evaluation skipped: {e}")
    
    def evaluate_rule(self, rule: AlertRule, db: Session):
        """Evaluate a single alert rule."""
        # Check cooldown
        last_eval = self.last_evaluation.get(rule.id)
        if last_eval:
            cooldown = timedelta(minutes=rule.cooldown_minutes)
            if datetime.utcnow() - last_eval < cooldown:
                return  # Still in cooldown period
        
        # Parse rule configuration
        try:
            config = json.loads(rule.rule_config)
        except json.JSONDecodeError:
            logger.error(f"Invalid rule config for rule {rule.id}")
            return
        
        # Evaluate based on rule type
        triggered = False
        message = ""
        context = {}
        
        if rule.rule_type == "PNL_THRESHOLD":
            triggered, message, context = self._evaluate_pnl_threshold(rule, config, db)
        elif rule.rule_type == "POSITION_SIZE":
            triggered, message, context = self._evaluate_position_size(rule, config, db)
        elif rule.rule_type == "DRAWDOWN":
            triggered, message, context = self._evaluate_drawdown(rule, config, db)
        elif rule.rule_type == "VOLATILITY":
            triggered, message, context = self._evaluate_volatility(rule, config, db)
        elif rule.rule_type == "CORRELATION":
            triggered, message, context = self._evaluate_correlation(rule, config, db)
        else:
            logger.warning(f"Unknown rule type: {rule.rule_type}")
            return
        
        # Update last evaluation time
        self.last_evaluation[rule.id] = datetime.utcnow()
        
        # Check if alert already exists (not acknowledged)
        if triggered:
            existing_alert = db.query(Alert).filter(
                Alert.rule_id == rule.id,
                Alert.status == "ACTIVE"
            ).first()
            
            if not existing_alert:
                # Create new alert
                alert = Alert(
                    rule_id=rule.id,
                    account_id=rule.account_id,
                    severity=rule.severity,
                    message=message,
                    context_json=json.dumps(context)
                )
                db.add(alert)
                db.flush()
                
                # Send notifications
                self._send_notifications(alert, rule, db)
                
                # Log to history
                history = AlertHistory(
                    alert_id=alert.id,
                    rule_id=rule.id,
                    account_id=rule.account_id,
                    event_type="TRIGGERED",
                    message=message,
                    context_json=json.dumps(context)
                )
                db.add(history)
                db.commit()
                
                logger.info(f"Alert triggered: {rule.name} for account {rule.account_id}")
    
    def _evaluate_pnl_threshold(self, rule: AlertRule, config: Dict, db: Session) -> tuple[bool, str, Dict]:
        """Evaluate P&L threshold rule."""
        threshold = config.get("threshold", 0)
        period = config.get("period", "daily")  # daily, weekly, monthly
        
        # Get latest P&L
        pnl = db.query(PnLHistory).filter(
            PnLHistory.account_id == rule.account_id
        ).order_by(desc(PnLHistory.date)).first()
        
        if not pnl:
            return False, "", {}
        
        total_pnl = pnl.total_pnl or 0
        
        # Check threshold (negative threshold means loss limit)
        triggered = total_pnl <= threshold
        
        message = f"P&L threshold breached: ${total_pnl:,.2f} (threshold: ${threshold:,.2f})"
        context = {
            "total_pnl": total_pnl,
            "threshold": threshold,
            "period": period,
            "date": pnl.date.isoformat() if pnl.date else None
        }
        
        return triggered, message, context
    
    def _evaluate_position_size(self, rule: AlertRule, config: Dict, db: Session) -> tuple[bool, str, Dict]:
        """Evaluate position size rule."""
        symbol = config.get("symbol")
        max_notional = config.get("max_notional", 0)
        
        # Get latest positions
        positions = db.query(Position).filter(
            Position.account_id == rule.account_id,
            Position.symbol == symbol if symbol else True
        ).order_by(desc(Position.timestamp)).all()
        
        triggered = False
        violating_positions = []
        
        for pos in positions:
            notional = abs((pos.market_value or 0) or (pos.quantity or 0) * (pos.market_price or 0))
            if notional > max_notional:
                triggered = True
                violating_positions.append({
                    "symbol": pos.symbol,
                    "notional": notional,
                    "max_notional": max_notional
                })
        
        if not triggered:
            return False, "", {}
        
        message = f"Position size limit exceeded for {len(violating_positions)} position(s)"
        context = {
            "violating_positions": violating_positions,
            "max_notional": max_notional
        }
        
        return True, message, context
    
    def _evaluate_drawdown(self, rule: AlertRule, config: Dict, db: Session) -> tuple[bool, str, Dict]:
        """Evaluate drawdown rule."""
        max_drawdown = config.get("max_drawdown", 0)  # e.g., 0.10 for 10%
        
        # Get P&L history
        pnl_records = db.query(PnLHistory).filter(
            PnLHistory.account_id == rule.account_id
        ).order_by(PnLHistory.date).all()
        
        if len(pnl_records) < 2:
            return False, "", {}
        
        # Calculate current drawdown
        net_liq_values = [r.net_liquidation or 0 for r in pnl_records]
        peak = max(net_liq_values)
        current = net_liq_values[-1]
        drawdown = (current - peak) / peak if peak > 0 else 0
        
        triggered = abs(drawdown) > max_drawdown
        
        message = f"Drawdown limit breached: {drawdown*100:.2f}% (limit: {max_drawdown*100:.2f}%)"
        context = {
            "drawdown": drawdown,
            "max_drawdown": max_drawdown,
            "peak": peak,
            "current": current
        }
        
        return triggered, message, context
    
    def _evaluate_volatility(self, rule: AlertRule, config: Dict, db: Session) -> tuple[bool, str, Dict]:
        """Evaluate volatility rule."""
        max_volatility = config.get("max_volatility", 0)  # e.g., 0.30 for 30%
        lookback_days = config.get("lookback_days", 30)
        
        # Get recent P&L history
        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)
        pnl_records = db.query(PnLHistory).filter(
            PnLHistory.account_id == rule.account_id,
            PnLHistory.date >= cutoff_date
        ).order_by(PnLHistory.date).all()
        
        if len(pnl_records) < 2:
            return False, "", {}
        
        # Calculate volatility (standard deviation of returns)
        import numpy as np
        net_liq_values = [r.net_liquidation or 0 for r in pnl_records]
        returns = np.diff(net_liq_values) / net_liq_values[:-1]
        volatility = np.std(returns) * np.sqrt(252)  # Annualized
        
        triggered = volatility > max_volatility
        
        message = f"Volatility limit breached: {volatility*100:.2f}% (limit: {max_volatility*100:.2f}%)"
        context = {
            "volatility": volatility,
            "max_volatility": max_volatility,
            "lookback_days": lookback_days
        }
        
        return triggered, message, context
    
    def _evaluate_correlation(self, rule: AlertRule, config: Dict, db: Session) -> tuple[bool, str, Dict]:
        """Evaluate correlation rule."""
        min_correlation = config.get("min_correlation", 0.7)
        symbols = config.get("symbols", [])
        
        if len(symbols) < 2:
            return False, "", {}
        
        # This is a simplified check - in production, you'd fetch market data
        # For now, we'll just return False as correlation requires market data
        # TODO: Implement correlation calculation with market data
        
        return False, "", {}
    
    def _send_notifications(self, alert: Alert, rule: AlertRule, db: Session):
        """Send notifications via configured channels."""
        channel_ids = [cid.strip() for cid in rule.channel_ids.split(",") if cid.strip()]
        
        if not channel_ids:
            return
        
        channels = db.query(AlertChannel).filter(
            AlertChannel.id.in_(channel_ids),
            AlertChannel.enabled == True
        ).all()
        
        # Send notifications asynchronously
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        for channel in channels:
            try:
                loop.run_until_complete(
                    self.notification_service.send_notification(channel, alert, rule)
                )
                alert.notifications_sent = True
                alert.notification_attempts += 1
                alert.last_notification_at = datetime.utcnow()
            except Exception as e:
                logger.error(f"Error sending notification via channel {channel.id}: {e}")
                alert.notification_attempts += 1
        
        db.commit()
    
    def acknowledge_alert(self, alert_id: int, acknowledged_by: str, db: Session):
        """Acknowledge an alert."""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return False
        
        alert.status = "ACKNOWLEDGED"
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = acknowledged_by
        
        # Log to history
        history = AlertHistory(
            alert_id=alert.id,
            rule_id=alert.rule_id,
            account_id=alert.account_id,
            event_type="ACKNOWLEDGED",
            message=f"Acknowledged by {acknowledged_by}",
            context_json=json.dumps({"acknowledged_by": acknowledged_by})
        )
        db.add(history)
        db.commit()
        
        return True
    
    def resolve_alert(self, alert_id: int, resolved_by: str, db: Session):
        """Resolve an alert."""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return False
        
        alert.status = "RESOLVED"
        alert.resolved_at = datetime.utcnow()
        
        # Log to history
        history = AlertHistory(
            alert_id=alert.id,
            rule_id=alert.rule_id,
            account_id=alert.account_id,
            event_type="RESOLVED",
            message=f"Resolved by {resolved_by}",
            context_json=json.dumps({"resolved_by": resolved_by})
        )
        db.add(history)
        db.commit()
        
        return True


# Global alert engine instance
alert_engine = AlertEngine()
