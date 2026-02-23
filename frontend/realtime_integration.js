// Real-time WebSocket integration for Dash frontend
// This script bridges WebSocket updates to Dash callbacks

(function() {
    'use strict';
    
    // Wait for Dash to be ready
    if (typeof window.dash_clientside === 'undefined') {
        console.warn('Dash clientside not available, WebSocket integration may not work');
        return;
    }
    
    // Initialize WebSocket when page loads
    document.addEventListener('DOMContentLoaded', function() {
        const apiBaseUrl = window.API_BASE_URL || 'http://localhost:8000/api';
        const accountId = window.ACCOUNT_ID || null;
        
        if (window.initRealtimeWebSocket) {
            const client = window.initRealtimeWebSocket(apiBaseUrl, accountId);
            
            // Update connection status
            client.on('connected', function() {
                updateConnectionStatus(true);
            });
            
            client.on('disconnected', function() {
                updateConnectionStatus(false);
            });
            
            // Handle position updates
            client.on('positions', function(data) {
                console.log('Position update received:', data);
                // Trigger Dash callback via custom event
                window.dispatchEvent(new CustomEvent('realtime-update', {
                    detail: { type: 'positions', data: data }
                }));
            });
            
            // Handle P&L updates
            client.on('pnl', function(data) {
                console.log('P&L update received:', data);
                window.dispatchEvent(new CustomEvent('realtime-update', {
                    detail: { type: 'pnl', data: data }
                }));
            });
            
            // Handle account updates
            client.on('account', function(data) {
                console.log('Account update received:', data);
                window.dispatchEvent(new CustomEvent('realtime-update', {
                    detail: { type: 'account', data: data }
                }));
            });
            
            // Store client globally for access
            window.realtimeClient = client;
        }
    });
    
    function updateConnectionStatus(connected) {
        const indicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('connection-status-text');
        
        if (indicator) {
            indicator.className = connected 
                ? 'status-indicator connected' 
                : 'status-indicator disconnected';
        }
        
        if (statusText) {
            statusText.textContent = connected ? 'Connected (Real-time)' : 'Disconnected';
        }
    }
})();
