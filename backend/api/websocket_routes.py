"""WebSocket routes for real-time data streaming."""
import asyncio
import json
import logging
import uuid
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from backend.websocket_manager import manager
from backend.realtime_broadcaster import broadcaster

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for real-time data streaming.
    
    Clients can subscribe to channels:
    - positions:{account_id} - Real-time position updates
    - pnl:{account_id} - Real-time P&L updates
    - account:{account_id} - Real-time account snapshot updates
    - trades:{account_id} - Real-time trade updates
    
    Message format for subscription:
    {
        "action": "subscribe",
        "channel": "positions:U1234567"
    }
    
    Message format for unsubscription:
    {
        "action": "unsubscribe",
        "channel": "positions:U1234567"
    }
    """
    connection_id = str(uuid.uuid4())
    await manager.connect(websocket, connection_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                action = message.get("action")
                channel = message.get("channel")
                
                if action == "subscribe" and channel:
                    await manager.subscribe(connection_id, channel)
                    await manager.send_personal_message({
                        "type": "subscription_confirmed",
                        "channel": channel,
                        "status": "subscribed"
                    }, connection_id)
                    
                elif action == "unsubscribe" and channel:
                    await manager.unsubscribe(connection_id, channel)
                    await manager.send_personal_message({
                        "type": "unsubscription_confirmed",
                        "channel": channel,
                        "status": "unsubscribed"
                    }, connection_id)
                    
                elif action == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": asyncio.get_event_loop().time()
                    }, connection_id)
                    
                else:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Unknown action: {action}"
                    }, connection_id)
                    
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, connection_id)
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}", exc_info=True)
                await manager.send_personal_message({
                    "type": "error",
                    "message": str(e)
                }, connection_id)
                
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        logger.info(f"WebSocket client disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(connection_id)


@router.websocket("/ws/{account_id}")
async def websocket_account_endpoint(websocket: WebSocket, account_id: str):
    """
    WebSocket endpoint for a specific account.
    Automatically subscribes to all channels for the account.
    """
    connection_id = str(uuid.uuid4())
    await manager.connect(websocket, connection_id)
    
    # Auto-subscribe to all account channels
    channels = [
        f"positions:{account_id}",
        f"pnl:{account_id}",
        f"account:{account_id}",
        f"trades:{account_id}",
    ]
    
    for channel in channels:
        await manager.subscribe(connection_id, channel)
    
    await manager.send_personal_message({
        "type": "connected",
        "account_id": account_id,
        "channels": channels,
        "message": "Subscribed to all account channels"
    }, connection_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": asyncio.get_event_loop().time()
                    }, connection_id)
                elif action == "request_update":
                    # Trigger manual update
                    await broadcaster.trigger_manual_update(account_id)
                    await manager.send_personal_message({
                        "type": "update_triggered",
                        "account_id": account_id
                    }, connection_id)
                else:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Unknown action: {action}"
                    }, connection_id)
                    
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, connection_id)
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}", exc_info=True)
                await manager.send_personal_message({
                    "type": "error",
                    "message": str(e)
                }, connection_id)
                
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        logger.info(f"WebSocket client disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(connection_id)
