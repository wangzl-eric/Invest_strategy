"""WebSocket client component for Dash frontend."""
import dash
from dash import html, dcc
import logging

logger = logging.getLogger(__name__)

# WebSocket client JavaScript
WEBSOCKET_CLIENT_JS = """
<script>
(function() {
    // WebSocket client for real-time updates
    class RealtimeWebSocketClient {
        constructor(url, accountId) {
            this.url = url;
            this.accountId = accountId;
            this.ws = null;
            this.reconnectAttempts = 0;
            this.maxReconnectAttempts = 10;
            this.reconnectDelay = 1000;
            this.listeners = {};
            this.connected = false;
        }
        
        connect() {
            try {
                const wsUrl = this.accountId 
                    ? `${this.url}/ws/${this.accountId}`
                    : `${this.url}/ws`;
                
                this.ws = new WebSocket(wsUrl.replace('http://', 'ws://').replace('https://', 'wss://'));
                
                this.ws.onopen = () => {
                    console.log('WebSocket connected');
                    this.connected = true;
                    this.reconnectAttempts = 0;
                    this.emit('connected', {});
                    
                    // Send ping periodically to keep connection alive
                    this.pingInterval = setInterval(() => {
                        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                            this.ws.send(JSON.stringify({ action: 'ping' }));
                        }
                    }, 30000); // Every 30 seconds
                };
                
                this.ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        this.handleMessage(data);
                    } catch (e) {
                        console.error('Error parsing WebSocket message:', e);
                    }
                };
                
                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.emit('error', { error: error });
                };
                
                this.ws.onclose = () => {
                    console.log('WebSocket disconnected');
                    this.connected = false;
                    this.emit('disconnected', {});
                    
                    if (this.pingInterval) {
                        clearInterval(this.pingInterval);
                    }
                    
                    // Attempt to reconnect
                    if (this.reconnectAttempts < this.maxReconnectAttempts) {
                        this.reconnectAttempts++;
                        setTimeout(() => {
                            console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);
                            this.connect();
                        }, this.reconnectDelay * this.reconnectAttempts);
                    }
                };
            } catch (e) {
                console.error('Error connecting WebSocket:', e);
                this.emit('error', { error: e });
            }
        }
        
        handleMessage(data) {
            const type = data.type;
            
            // Emit specific event types
            if (type === 'positions_update') {
                this.emit('positions', data);
            } else if (type === 'pnl_update') {
                this.emit('pnl', data);
            } else if (type === 'account_update') {
                this.emit('account', data);
            } else if (type === 'trades_update') {
                this.emit('trades', data);
            } else {
                // Emit generic message
                this.emit('message', data);
            }
            
            // Also emit by type
            this.emit(type, data);
        }
        
        on(event, callback) {
            if (!this.listeners[event]) {
                this.listeners[event] = [];
            }
            this.listeners[event].push(callback);
        }
        
        off(event, callback) {
            if (this.listeners[event]) {
                this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
            }
        }
        
        emit(event, data) {
            if (this.listeners[event]) {
                this.listeners[event].forEach(callback => {
                    try {
                        callback(data);
                    } catch (e) {
                        console.error('Error in event listener:', e);
                    }
                });
            }
        }
        
        subscribe(channel) {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({
                    action: 'subscribe',
                    channel: channel
                }));
            }
        }
        
        unsubscribe(channel) {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({
                    action: 'unsubscribe',
                    channel: channel
                }));
            }
        }
        
        requestUpdate() {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({
                    action: 'request_update'
                }));
            }
        }
        
        disconnect() {
            if (this.pingInterval) {
                clearInterval(this.pingInterval);
            }
            if (this.ws) {
                this.ws.close();
            }
        }
    }
    
    // Initialize WebSocket client
    window.realtimeClient = null;
    
    function initWebSocket(apiBaseUrl, accountId) {
        if (window.realtimeClient) {
            window.realtimeClient.disconnect();
        }
        
        window.realtimeClient = new RealtimeWebSocketClient(apiBaseUrl, accountId);
        window.realtimeClient.connect();
        
        return window.realtimeClient;
    }
    
    // Make it available globally
    window.initRealtimeWebSocket = initWebSocket;
    
    // Auto-initialize if API_BASE_URL is available
    if (typeof window.API_BASE_URL !== 'undefined') {
        const accountId = window.ACCOUNT_ID || null;
        window.initRealtimeWebSocket(window.API_BASE_URL, accountId);
    }
})();
</script>
"""


def create_websocket_client_component(api_base_url: str = "http://localhost:8000/api", account_id: str = None):
    """Create a Dash component that includes the WebSocket client JavaScript."""
    # Read the integration script
    import os
    integration_script_path = os.path.join(os.path.dirname(__file__), 'realtime_integration.js')
    integration_script = ""
    if os.path.exists(integration_script_path):
        with open(integration_script_path, 'r') as f:
            integration_script = f.read()
    
    return html.Div([
        html.Script(
            children=f"""
            window.API_BASE_URL = '{api_base_url}';
            window.ACCOUNT_ID = {f"'{account_id}'" if account_id else 'null'};
            """,
            type="text/javascript"
        ),
        html.Script(
            children=WEBSOCKET_CLIENT_JS,
            type="text/javascript"
        ),
        html.Script(
            children=integration_script,
            type="text/javascript"
        ) if integration_script else html.Div(),
        html.Div(id="websocket-status", style={"display": "none"}),  # Hidden status indicator
    ])
