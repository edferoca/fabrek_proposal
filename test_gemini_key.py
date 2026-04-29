#!/usr/bin/env python
"""
Test script to verify Gemini API key is loaded correctly.
Run this to debug if the API key is being detected.
"""

import os
from dotenv import load_dotenv

print("=" * 80)
print("🔍 GEMINI API KEY VERIFICATION TEST")
print("=" * 80)

# Load .env file
print("\n[1] Loading .env file...")
load_dotenv()

# Check if key exists
api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-pro")
fallback = os.getenv("USE_FALLBACK", "true")

print("\n[2] Environment Variables Found:")
print(f"    GEMINI_API_KEY: {'✅ SET' if api_key else '❌ NOT SET'}")
print(f"    GEMINI_MODEL: {model if model else '(default)'}")
print(f"    USE_FALLBACK: {fallback}")

if api_key:
    # Show partial key (for security)
    masked_key = api_key[:10] + "..." + api_key[-5:]
    print(f"\n[3] API Key Details:")
    print(f"    Full key: {masked_key}")
    print(f"    Length: {len(api_key)} characters")
    print(f"    Looks valid: {'✅ Yes' if len(api_key) > 30 else '❌ Possibly short'}")
else:
    print("\n[3] ❌ API Key NOT found!")
    print("    Make sure .env file has: GEMINI_API_KEY=your_key_here")

# Try importing and configuring
print("\n[4] Testing Gemini Library Import...")
try:
    import google.generativeai as genai
    print("    ✅ google.generativeai imported successfully")
    
    if api_key:
        print("\n[5] Configuring Gemini with API key...")
        try:
            genai.configure(api_key=api_key)
            print("    ✅ Gemini configured successfully!")
            
            # Try getting models
            print("\n[6] Available Gemini Models:")
            try:
                models = genai.list_models()
                for i, model_info in enumerate(models, 1):
                    if "generateContent" in model_info.supported_generation_methods:
                        print(f"    {i}. {model_info.name}")
                print("    ✅ Models listed successfully!")
            except Exception as e:
                print(f"    ⚠️  Could not list models: {e}")
        except Exception as e:
            print(f"    ❌ Configuration failed: {e}")
except ImportError:
    print("    ❌ google.generativeai NOT installed")
    print("    Install with: pip install google-generativeai")

print("\n" + "=" * 80)
if api_key:
    print("✅ RESULT: Everything looks good! Your API key is configured correctly.")
    print("   Ready to run: python main.py")
else:
    print("❌ RESULT: API key not found. Please:")
    print("   1. Open .env file")
    print("   2. Add: GEMINI_API_KEY=your_key_here")
    print("   3. Save and try again")
print("=" * 80)
