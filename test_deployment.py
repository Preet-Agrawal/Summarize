#!/usr/bin/env python3
"""
Test script to verify deployment fixes work correctly
"""
import os
import sys
from unittest.mock import patch

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_startup_without_mongo():
    """Test that the app can start even when MongoDB is unavailable"""
    print("Testing app startup without MongoDB...")
    
    # Mock environment variables for testing
    test_env = {
        'MONGO_URI': 'mongodb://invalid-host:27017/test',
        'SECRET_KEY': 'test-secret-key',
        'FLASK_ENV': 'production',
        'HUGGINGFACE_API_KEY': 'test-key'
    }
    
    with patch.dict(os.environ, test_env):
        try:
            # Import the app (this will trigger the MongoDB connection attempt)
            from app import app, mongo_connected
            
            print(f"✓ App imported successfully")
            print(f"✓ MongoDB connected: {mongo_connected}")
            
            # Test that the app can handle requests
            with app.test_client() as client:
                response = client.get('/test')
                assert response.status_code == 200
                print("✓ Test endpoint working")
                
                response = client.get('/')
                assert response.status_code == 200
                print("✓ Home page working")
                
            print("✓ All tests passed! App can run without MongoDB.")
            return True
            
        except Exception as e:
            print(f"✗ Test failed: {e}")
            return False

if __name__ == "__main__":
    success = test_app_startup_without_mongo()
    sys.exit(0 if success else 1)
