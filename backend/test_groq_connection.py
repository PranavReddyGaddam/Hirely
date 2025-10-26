#!/usr/bin/env python3
"""
Test script to verify Groq API connection
Run this to diagnose AI insights issues
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("🔍 GROQ API CONNECTION TEST")
print("=" * 60)
print()

# Step 1: Check environment variable
print("Step 1: Checking environment variables...")
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    print("❌ GROQ_API_KEY not found in environment variables")
    print("💡 Please add GROQ_API_KEY to your .env file")
    print()
    sys.exit(1)
else:
    print(f"✅ GROQ_API_KEY found: {groq_api_key[:10]}...{groq_api_key[-4:]}")
    print()

# Step 2: Test Groq service initialization
print("Step 2: Initializing Groq service...")
try:
    from app.services.groq_service import GroqService
    
    groq_service = GroqService()
    
    if not groq_service.client:
        print("❌ Groq client failed to initialize")
        print("💡 Check if your API key is valid")
        sys.exit(1)
    else:
        print("✅ Groq service initialized successfully")
        print()
except Exception as e:
    print(f"❌ Error initializing Groq service: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Test API connection
print("Step 3: Testing Groq API connection...")
print("   (This will make a minimal API call)")
print()

try:
    result = groq_service.test_connection()
    
    if result.get("success"):
        print("✅ Groq API connection successful!")
        print(f"   Model: {result.get('model', 'unknown')}")
        print(f"   Message: {result.get('message', 'unknown')}")
        print()
        print("=" * 60)
        print("🎉 ALL TESTS PASSED - AI Insights should work!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ Groq API connection failed")
        print(f"   Error: {result.get('error', 'unknown')}")
        print()
        print("Troubleshooting:")
        print("  1. Verify your API key at https://console.groq.com")
        print("  2. Check if you have API credits/quota remaining")
        print("  3. Verify network connectivity")
        print("  4. Check Groq service status")
        print()
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Unexpected error during API test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
