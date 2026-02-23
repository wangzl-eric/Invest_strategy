#!/usr/bin/env python3
"""
IBKR API Setup Guide Script

This script provides guidance on setting up IBKR API access.
"""

print("=" * 70)
print("IBKR API Setup Guide")
print("=" * 70)
print()
print("To use this application, you need to set up IBKR API access:")
print()
print("1. INSTALL TWS OR IB GATEWAY")
print("   - Download TWS (Trader Workstation) or IB Gateway from:")
print("     https://www.interactivebrokers.com/en/index.php?f=16042")
print("   - Install and launch the application")
print()
print("2. ENABLE API ACCESS")
print("   - In TWS: Configure -> API -> Settings")
print("   - Enable 'Enable ActiveX and Socket Clients'")
print("   - Set 'Socket port' to 7497 (paper) or 7496 (live)")
print("   - Add '127.0.0.1' to 'Trusted IPs'")
print("   - Click 'OK' and restart TWS/Gateway")
print()
print("3. CONFIGURE APPLICATION")
print("   - Update config/app_config.yaml with your settings:")
print("     * host: '127.0.0.1' (default)")
print("     * port: 7497 for paper trading, 7496 for live trading")
print("     * client_id: Any unique integer (default: 1)")
print()
print("4. TEST CONNECTION")
print("   - Make sure TWS/Gateway is running")
print("   - Run: python -m backend.ibkr_client")
print()
print("5. SECURITY NOTES")
print("   - Never commit API credentials to version control")
print("   - Use environment variables for sensitive data")
print("   - Keep TWS/Gateway updated")
print()
print("=" * 70)

