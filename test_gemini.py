#!/usr/bin/env python3

import os
from langchain_google_genai import ChatGoogleGenerativeAI

def test_gemini_api():
    """Test the Gemini API integration"""
    
    # Check if API key is set
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY environment variable not set!")
        return False
    
    print("✅ GOOGLE_API_KEY environment variable found")
    print(f"🔑 API Key: {api_key[:8]}...{api_key[-8:]}")  # Show partial key for verification
    
    try:
        # Initialize Gemini model - Free tier with Gemini 2.0 Flash-Lite (most cost-effective)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            google_api_key=api_key,
            temperature=0.7
        )
        
        # Test a simple query
        response = llm.invoke("Hello! Can you briefly introduce yourself?")
        print("✅ Gemini API connection successful!")
        print(f"🤖 Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Gemini API: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Gemini API integration...")
    success = test_gemini_api()
    if success:
        print("\n🎉 Gemini API is ready to use!")
    else:
        print("\n💥 Gemini API test failed. Please check your configuration.")
