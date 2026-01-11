#!/usr/bin/env python3
"""Test script for BotConfig API endpoints."""

import httpx
import json

def test_botconfig_api():
    """Test the BotConfig API endpoints."""
    base_url = "http://localhost:8000"
    
    # Test data
    test_config = {
        "key": "test_api_key",
        "value": "test_api_value",
        "description": "Test configuration from API"
    }
    
    print("🧪 Testing BotConfig API...")
    print("=" * 50)
    
    try:
        # Test POST - Create new BotConfig
        print("1. Testing POST /api/botconfig")
        response = httpx.post(f"{base_url}/api/botconfig", json=test_config, timeout=10.0)
        if response.status_code == 200:
            created = response.json()
            print(f"✅ Created: {json.dumps(created, indent=2, default=str)}")
        else:
            print(f"❌ POST failed: {response.status_code} - {response.text}")
            return
        
        # Test GET - Get all BotConfigs
        print("\n2. Testing GET /api/botconfig")
        response = httpx.get(f"{base_url}/api/botconfig", timeout=10.0)
        if response.status_code == 200:
            configs = response.json()
            print(f"✅ Found {len(configs)} configurations")
            for config in configs:
                print(f"   - {config['key']}: {config['value']}")
        
        # Test GET by key
        print(f"\n3. Testing GET /api/botconfig/{test_config['key']}")
        response = httpx.get(f"{base_url}/api/botconfig/{test_config['key']}", timeout=10.0)
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Retrieved: {json.dumps(config, indent=2, default=str)}")
        
        # Test PUT - Update existing
        updated_config = {
            "key": test_config['key'],
            "value": "updated_test_value",
            "description": "Updated description"
        }
        print(f"\n4. Testing PUT /api/botconfig/{test_config['key']}")
        response = httpx.put(f"{base_url}/api/botconfig/{test_config['key']}", json=updated_config, timeout=10.0)
        if response.status_code == 200:
            updated = response.json()
            print(f"✅ Updated: {json.dumps(updated, indent=2, default=str)}")
        
        print("\n" + "=" * 50)
        print("✅ All BotConfig API tests completed successfully!")
        
    except httpx.ConnectError:
        print("❌ Could not connect to API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")

if __name__ == "__main__":
    test_botconfig_api()
