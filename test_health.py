#!/usr/bin/env python3
"""
Simple test script to verify health check endpoint works
"""

import requests
import sys

def test_health_check(url):
    try:
        response = requests.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed with error: {e}")
        return False

if __name__ == "__main__":
    # Test local health check
    url = "http://localhost:8000"
    print(f"Testing health check at {url}/health")
    success = test_health_check(url)
    sys.exit(0 if success else 1)
