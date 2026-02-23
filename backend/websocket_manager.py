"""WebSocket connection manager for real-time data streaming."""
import asyncio
import json
import logging
from typing import Dict, Set, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts messages."""
    
    def __init__(self):
        # Map of connection_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # Map of connection_id -> set of subscribed channels
        self.subscriptions: Dict[str, Set[str]] = {}
        # Map of channel -> set of connection_ids
        self.channel_subscribers: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, connection_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        self.subscriptions[connection_id] = set()
        logger.info(f"WebSocket connection established: {connection_id}")
    
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Remove from all channel subscriptions
        if connection_id in self.subscriptions:
            for channel in self.subscriptions[connection_id]:
                if channel in self.channel_subscribers:
                    self.channel_subscribers[channel].discard(connection_id)
            del self.subscriptions[connection_id]
        
        logger.info(f"WebSocket connection closed: {connection_id}")
    
    async def subscribe(self, connection_id: str, channel: str):
        """Subscribe a connection to a channel."""
        if connection_id not in self.active_connections:
            return False
        
        self.subscriptions[connection_id].add(channel)
        if channel not in self.channel_subscribers:
            self.channel_subscribers[channel] = set()
        self.channel_subscribers[channel].add(connection_id)
        logger.debug(f"Connection {connection_id} subscribed to {channel}")
        return True
    
    async def unsubscribe(self, connection_id: str, channel: str):
        """Unsubscribe a connection from a channel."""
        if connection_id in self.subscriptions:
            self.subscriptions[connection_id].discard(channel)
        if channel in self.channel_subscribers:
            self.channel_subscribers[channel].discard(connection_id)
        logger.debug(f"Connection {connection_id} unsubscribed from {channel}")
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """Send a message to a specific connection."""
        if connection_id not in self.active_connections:
            return False
        
        websocket = self.active_connections[connection_id]
        try:
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {e}")
            return False
    
    async def broadcast_to_channel(self, message: dict, channel: str):
        """Broadcast a message to all subscribers of a channel."""
        if channel not in self.channel_subscribers:
            return 0
        
        subscribers = self.channel_subscribers[channel].copy()
        sent_count = 0
        disconnected = []
        
        for connection_id in subscribers:
            if connection_id in self.active_connections:
                try:
                    await self.active_connections[connection_id].send_json(message)
                    sent_count += 1
                except Exception as e:
                    logger.warning(f"Error broadcasting to {connection_id}: {e}")
                    disconnected.append(connection_id)
            else:
                disconnected.append(connection_id)
        
        # Clean up disconnected clients
        for connection_id in disconnected:
            self.disconnect(connection_id)
        
        return sent_count
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all connected clients."""
        disconnected = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Error broadcasting to {connection_id}: {e}")
                disconnected.append(connection_id)
        
        # Clean up disconnected clients
        for connection_id in disconnected:
            self.disconnect(connection_id)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)
    
    def get_channel_subscriber_count(self, channel: str) -> int:
        """Get the number of subscribers to a channel."""
        return len(self.channel_subscribers.get(channel, set()))


# Global connection manager instance
manager = ConnectionManager()
