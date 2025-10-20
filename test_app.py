#!/usr/bin/env python3
"""
Test script to verify the application can start without errors
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test basic Flask import
        from flask import Flask
        print("✅ Flask imported successfully")
        
        # Test app import
        from app import app
        print("✅ App imported successfully")
        
        # Test wsgi import
        from wsgi import application
        print("✅ WSGI application imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_health_endpoint():
    """Test that health endpoint works"""
    try:
        from app import app
        
        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Health endpoint works")
                return True
            else:
                print(f"❌ Health endpoint failed with status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing TrinityAI application...")
    
    success = True
    success &= test_imports()
    success &= test_health_endpoint()
    
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
