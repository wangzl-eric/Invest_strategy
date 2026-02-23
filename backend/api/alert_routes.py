"""API routes for alert management."""
import logging
import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from backend.database import get_db
from backend.models import AlertRule, Alert, AlertHistory, AlertChannel
from backend.api.schemas import (
    AlertRuleCreate, AlertRuleUpdate, AlertRuleResponse,
    AlertResponse, AlertHistoryResponse,
    AlertChannelCreate, AlertChannelUpdate, AlertChannelResponse
)
from backend.alert_engine import AlertEngine
from backend.notifications import NotificationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["alerts"])

alert_engine = AlertEngine()
notification_service = NotificationService()


def model_to_dict(model_instance, exclude_fields: Optional[List[str]] = None):
    """Convert SQLAlchemy model to dict."""
    exclude_fields = exclude_fields or []
    result = {}
    for c in model_instance.__table__.columns:
        if c.name not in exclude_fields:
            value = getattr(model_instance, c.name)
            result[c.name] = value
    return result


# =============================================================================
# Alert Rules
# =============================================================================

@router.post("/rules", response_model=AlertRuleResponse, status_code=201)
async def create_alert_rule(
    rule_data: AlertRuleCreate,
    db: Session = Depends(get_db)
):
    """Create a new alert rule."""
    try:
        # Convert channel_ids list to comma-separated string
        channel_ids_str = ",".join(str(cid) for cid in rule_data.channel_ids)
        escalation_channel_ids_str = ",".join(str(cid) for cid in rule_data.escalation_channel_ids)
        
        rule = AlertRule(
            account_id=rule_data.account_id,
            name=rule_data.name,
            description=rule_data.description,
            rule_type=rule_data.rule_type,
            rule_config=json.dumps(rule_data.rule_config),
            severity=rule_data.severity,
            channel_ids=channel_ids_str,
            cooldown_minutes=rule_data.cooldown_minutes,
            escalation_enabled=rule_data.escalation_enabled,
            escalation_after_minutes=rule_data.escalation_after_minutes,
            escalation_channel_ids=escalation_channel_ids_str,
            enabled=True
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        
        # Convert response
        rule_dict = model_to_dict(rule)
        rule_dict['rule_config'] = json.loads(rule.rule_config)
        return AlertRuleResponse(**rule_dict)
    except Exception as e:
        logger.error(f"Error creating alert rule: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules", response_model=List[AlertRuleResponse])
async def list_alert_rules(
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
    db: Session = Depends(get_db)
):
    """List all alert rules."""
    try:
        query = db.query(AlertRule)
        
        if account_id:
            query = query.filter(AlertRule.account_id == account_id)
        if enabled is not None:
            query = query.filter(AlertRule.enabled == enabled)
        
        rules = query.order_by(desc(AlertRule.created_at)).all()
        
        result = []
        for rule in rules:
            rule_dict = model_to_dict(rule)
            rule_dict['rule_config'] = json.loads(rule.rule_config)
            result.append(AlertRuleResponse(**rule_dict))
        
        return result
    except Exception as e:
        logger.error(f"Error listing alert rules: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules/{rule_id}", response_model=AlertRuleResponse)
async def get_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific alert rule."""
    try:
        rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="Alert rule not found")
        
        rule_dict = model_to_dict(rule)
        rule_dict['rule_config'] = json.loads(rule.rule_config)
        return AlertRuleResponse(**rule_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alert rule: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: int,
    rule_data: AlertRuleUpdate,
    db: Session = Depends(get_db)
):
    """Update an alert rule."""
    try:
        rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="Alert rule not found")
        
        if rule_data.name is not None:
            rule.name = rule_data.name
        if rule_data.description is not None:
            rule.description = rule_data.description
        if rule_data.rule_config is not None:
            rule.rule_config = json.dumps(rule_data.rule_config)
        if rule_data.severity is not None:
            rule.severity = rule_data.severity
        if rule_data.channel_ids is not None:
            rule.channel_ids = ",".join(str(cid) for cid in rule_data.channel_ids)
        if rule_data.enabled is not None:
            rule.enabled = rule_data.enabled
        if rule_data.cooldown_minutes is not None:
            rule.cooldown_minutes = rule_data.cooldown_minutes
        if rule_data.escalation_enabled is not None:
            rule.escalation_enabled = rule_data.escalation_enabled
        if rule_data.escalation_after_minutes is not None:
            rule.escalation_after_minutes = rule_data.escalation_after_minutes
        if rule_data.escalation_channel_ids is not None:
            rule.escalation_channel_ids = ",".join(str(cid) for cid in rule_data.escalation_channel_ids)
        
        rule.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(rule)
        
        rule_dict = model_to_dict(rule)
        rule_dict['rule_config'] = json.loads(rule.rule_config)
        return AlertRuleResponse(**rule_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating alert rule: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/rules/{rule_id}", status_code=204)
async def delete_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """Delete an alert rule."""
    try:
        rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="Alert rule not found")
        
        db.delete(rule)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting alert rule: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Alerts
# =============================================================================

@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE, ACKNOWLEDGED, RESOLVED)"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(100, description="Maximum number of alerts to return"),
    db: Session = Depends(get_db)
):
    """List all alerts."""
    try:
        query = db.query(Alert)
        
        if account_id:
            query = query.filter(Alert.account_id == account_id)
        if status:
            query = query.filter(Alert.status == status)
        if severity:
            query = query.filter(Alert.severity == severity)
        
        alerts = query.order_by(desc(Alert.created_at)).limit(limit).all()
        
        result = []
        for alert in alerts:
            alert_dict = model_to_dict(alert)
            alert_dict['context'] = json.loads(alert.context_json)
            result.append(AlertResponse(**alert_dict))
        
        return result
    except Exception as e:
        logger.error(f"Error listing alerts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific alert."""
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert_dict = model_to_dict(alert)
        alert_dict['context'] = json.loads(alert.context_json)
        return AlertResponse(**alert_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: int,
    acknowledged_by: Optional[str] = Query(None, description="User who acknowledged the alert"),
    db: Session = Depends(get_db)
):
    """Acknowledge an alert."""
    try:
        success = alert_engine.acknowledge_alert(alert_id, acknowledged_by)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        alert_dict = model_to_dict(alert)
        alert_dict['context'] = json.loads(alert.context_json)
        return AlertResponse(**alert_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """Resolve an alert."""
    try:
        success = alert_engine.resolve_alert(alert_id)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        alert_dict = model_to_dict(alert)
        alert_dict['context'] = json.loads(alert.context_json)
        return AlertResponse(**alert_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate", status_code=200)
async def evaluate_rules(
    account_id: Optional[str] = Query(None, description="Account ID to evaluate rules for"),
    db: Session = Depends(get_db)
):
    """Manually trigger evaluation of all alert rules."""
    try:
        alerts = alert_engine.evaluate_all_rules(account_id)
        
        # Send notifications for triggered alerts
        for alert in alerts:
            try:
                await notification_service.send_alert_notifications(alert)
            except Exception as e:
                logger.error(f"Error sending notifications for alert {alert.id}: {e}", exc_info=True)
        
        return {
            "evaluated": True,
            "alerts_triggered": len(alerts),
            "alert_ids": [a.id for a in alerts]
        }
    except Exception as e:
        logger.error(f"Error evaluating rules: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{alert_id}/history", response_model=List[AlertHistoryResponse])
async def get_alert_history(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """Get history for a specific alert."""
    try:
        history = db.query(AlertHistory).filter(
            AlertHistory.alert_id == alert_id
        ).order_by(AlertHistory.created_at).all()
        
        result = []
        for h in history:
            h_dict = model_to_dict(h)
            h_dict['context'] = json.loads(h.context_json) if h.context_json else {}
            result.append(AlertHistoryResponse(**h_dict))
        
        return result
    except Exception as e:
        logger.error(f"Error getting alert history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Alert Channels
# =============================================================================

@router.post("/channels", response_model=AlertChannelResponse, status_code=201)
async def create_alert_channel(
    channel_data: AlertChannelCreate,
    db: Session = Depends(get_db)
):
    """Create a new alert channel."""
    try:
        channel = AlertChannel(
            account_id=channel_data.account_id,
            name=channel_data.name,
            channel_type=channel_data.channel_type,
            config_json=json.dumps(channel_data.config),
            enabled=channel_data.enabled
        )
        db.add(channel)
        db.commit()
        db.refresh(channel)
        
        channel_dict = model_to_dict(channel)
        channel_dict['config'] = json.loads(channel.config_json)
        del channel_dict['config_json']
        return AlertChannelResponse(**channel_dict)
    except Exception as e:
        logger.error(f"Error creating alert channel: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/channels", response_model=List[AlertChannelResponse])
async def list_alert_channels(
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
    db: Session = Depends(get_db)
):
    """List all alert channels."""
    try:
        query = db.query(AlertChannel)
        
        if account_id:
            query = query.filter(AlertChannel.account_id == account_id)
        if enabled is not None:
            query = query.filter(AlertChannel.enabled == enabled)
        
        channels = query.order_by(desc(AlertChannel.created_at)).all()
        
        result = []
        for channel in channels:
            channel_dict = model_to_dict(channel)
            channel_dict['config'] = json.loads(channel.config_json)
            del channel_dict['config_json']
            result.append(AlertChannelResponse(**channel_dict))
        
        return result
    except Exception as e:
        logger.error(f"Error listing alert channels: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/channels/{channel_id}", response_model=AlertChannelResponse)
async def get_alert_channel(
    channel_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific alert channel."""
    try:
        channel = db.query(AlertChannel).filter(AlertChannel.id == channel_id).first()
        if not channel:
            raise HTTPException(status_code=404, detail="Alert channel not found")
        
        channel_dict = model_to_dict(channel)
        channel_dict['config'] = json.loads(channel.config_json)
        del channel_dict['config_json']
        return AlertChannelResponse(**channel_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alert channel: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/channels/{channel_id}", response_model=AlertChannelResponse)
async def update_alert_channel(
    channel_id: int,
    channel_data: AlertChannelUpdate,
    db: Session = Depends(get_db)
):
    """Update an alert channel."""
    try:
        channel = db.query(AlertChannel).filter(AlertChannel.id == channel_id).first()
        if not channel:
            raise HTTPException(status_code=404, detail="Alert channel not found")
        
        if channel_data.name is not None:
            channel.name = channel_data.name
        if channel_data.config is not None:
            channel.config_json = json.dumps(channel_data.config)
        if channel_data.enabled is not None:
            channel.enabled = channel_data.enabled
        
        channel.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(channel)
        
        channel_dict = model_to_dict(channel)
        channel_dict['config'] = json.loads(channel.config_json)
        del channel_dict['config_json']
        return AlertChannelResponse(**channel_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating alert channel: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/channels/{channel_id}", status_code=204)
async def delete_alert_channel(
    channel_id: int,
    db: Session = Depends(get_db)
):
    """Delete an alert channel."""
    try:
        channel = db.query(AlertChannel).filter(AlertChannel.id == channel_id).first()
        if not channel:
            raise HTTPException(status_code=404, detail="Alert channel not found")
        
        db.delete(channel)
        db.commit()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting alert channel: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
