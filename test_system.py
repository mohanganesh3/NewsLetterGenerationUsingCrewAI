#!/usr/bin/env python3
"""
Test script to verify Newsletter Generation is working with Google API
"""

import os
import sys
sys.path.append('src')

def test_environment():
    """Test environment variables"""
    print("🔧 Testing Environment Variables...")
    
    exa_key = os.getenv('EXA_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    print(f"  EXA_API_KEY: {'✓ Set' if exa_key else '✗ Not set'}")
    print(f"  GOOGLE_API_KEY: {'✓ Set' if google_key else '✗ Not set'}")
    
    return bool(exa_key and google_key)

def test_imports():
    """Test all imports"""
    print("\n📦 Testing Imports...")
    
    try:
        from newsletter_gen.crew import NewsletterGenCrew
        print("  ✓ NewsletterGenCrew imported successfully")
        
        from newsletter_gen.tools.research import SearchAndContents, FindSimilar, GetContents
        print("  ✓ Research tools imported successfully")
        
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("  ✓ Google Gemini imported successfully")
        
        return True
    except Exception as e:
        print(f"  ✗ Import error: {e}")
        return False

def test_crew_creation():
    """Test crew creation"""
    print("\n🤖 Testing Crew Creation...")
    
    try:
        from newsletter_gen.crew import NewsletterGenCrew
        crew_instance = NewsletterGenCrew()
        print("  ✓ Crew instance created successfully")
        
        crew = crew_instance.crew()
        print("  ✓ Crew assembled successfully")
        
        return True
    except Exception as e:
        print(f"  ✗ Crew creation error: {e}")
        return False

def test_google_llm():
    """Test Google LLM initialization"""
    print("\n🧠 Testing Google Gemini LLM...")
    
    try:
        from newsletter_gen.crew import NewsletterGenCrew
        crew_instance = NewsletterGenCrew()
        llm = crew_instance.llm()
        print("  ✓ Google Gemini LLM initialized successfully")
        print(f"  ✓ Model: {getattr(llm, 'model_name', getattr(llm, 'model', 'Unknown'))}")
        
        return True
    except Exception as e:
        print(f"  ✗ LLM initialization error: {e}")
        return False

def main():
    print("🚀 Newsletter Generation Test Suite")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    tests = [
        test_environment,
        test_imports,
        test_crew_creation,
        test_google_llm
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The Newsletter Generation system is ready to use.")
        print("\n📱 Usage Options:")
        print("  1. Web Interface: http://localhost:8501")
        print("  2. Command Line: poetry run newsletter_gen")
        print("\n🔑 API Configuration:")
        print("  ✓ Using Google Gemini 1.5 Flash")
        print("  ✓ Using Exa for web search")
    else:
        print(f"\n❌ {total - passed} test(s) failed. Please check the configuration.")

if __name__ == "__main__":
    main()
