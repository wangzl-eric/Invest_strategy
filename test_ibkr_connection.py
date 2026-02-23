#!/usr/bin/env python3
"""Test IBKR TWS/Gateway connection."""
import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.ibkr_client import IBKRClient
from backend.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_connection():
    """Test connection to IBKR TWS/Gateway."""
    print("=" * 70)
    print("IBKR Connection Test")
    print("=" * 70)
    print()
    
    print(f"Configuration:")
    print(f"  Host: {settings.ibkr.host}")
    print(f"  Port: {settings.ibkr.port}")
    print(f"  Client ID: {settings.ibkr.client_id}")
    print(f"  Timeout: {settings.ibkr.timeout}s")
    print()
    
    # Check if port is accessible
    import socket
    print("Checking if port is accessible...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((settings.ibkr.host, settings.ibkr.port))
    sock.close()
    
    if result == 0:
        print(f"✅ Port {settings.ibkr.port} is open and accessible")
    else:
        print(f"❌ Port {settings.ibkr.port} is NOT accessible")
        print()
        print("Troubleshooting steps:")
        print("  1. Make sure TWS/Gateway is running")
        print("  2. Check that API is enabled in TWS/Gateway:")
        print("     - Configure → API → Settings")
        print("     - Enable 'Enable ActiveX and Socket Clients'")
        print(f"     - Set Socket port to {settings.ibkr.port}")
        print("     - Add '127.0.0.1' to Trusted IPs")
        print("  3. Restart TWS/Gateway after changing settings")
        print("  4. Check firewall settings")
        return False
    
    print()
    print("Attempting to connect to IBKR...")
    
    client = IBKRClient()
    
    try:
        connected = await client.connect()
        
        if connected:
            print("✅ Successfully connected to IBKR!")
            print()
            
            # Try to get account summary
            print("Testing data retrieval...")
            try:
                account_summary = await client.get_account_summary()
                print("✅ Successfully retrieved account data!")
                print()
                print("Account Summary:")
                for key, value in account_summary.items():
                    if isinstance(value, float):
                        print(f"  {key}: ${value:,.2f}")
                    else:
                        print(f"  {key}: {value}")
                
                account_id = account_summary.get('AccountId')
                if account_id:
                    print()
                    print(f"Your Account ID: {account_id}")
                    print()
                    print("You can use this account ID when fetching data:")
                    print(f"  curl -X POST 'http://localhost:8000/api/fetch-data?account_id={account_id}'")
                
            except Exception as e:
                print(f"⚠️  Connected but error retrieving data: {e}")
                print("This might be normal if you don't have positions yet.")
            
            await client.disconnect()
            print()
            print("=" * 70)
            print("Connection test completed successfully!")
            print("=" * 70)
            return True
        else:
            print("❌ Failed to connect to IBKR")
            print()
            print("Possible issues:")
            print("  1. TWS/Gateway is not running")
            print("  2. API is not enabled in TWS/Gateway")
            print(f"  3. Port {settings.ibkr.port} doesn't match TWS/Gateway port")
            print("  4. '127.0.0.1' is not in Trusted IPs")
            print("  5. TWS/Gateway needs to be restarted after enabling API")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Verify TWS/Gateway is running and logged in")
        print("  2. Check API settings in TWS/Gateway")
        print(f"  3. Verify port {settings.ibkr.port} matches TWS/Gateway port")
        print("  4. Make sure you're logged into TWS/Gateway")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_connection())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)

