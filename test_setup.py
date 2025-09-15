#!/usr/bin/env python3
"""
Test script to verify Newsletter Generation functionality
"""

import os
import sys
sys.path.append('src')

from newsletter_gen.crew import NewsletterGenCrew

def test_basic_setup():
    """Test basic setup and imports"""
    print("Testing basic setup...")
    
    # Check environment variables
    exa_key = os.getenv('EXA_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    print(f"EXA_API_KEY: {'✓ Set' if exa_key else '✗ Not set'}")
    print(f"GOOGLE_API_KEY: {'✓ Set' if google_key else '✗ Not set'}")
    
    # Try to initialize the crew
    try:
        crew = NewsletterGenCrew()
        print("✓ NewsletterGenCrew initialized successfully")
        
        # Try to access the crew method
        crew_instance = crew.crew()
        print("✓ Crew instance created successfully")
        
        print("\n✅ Basic setup test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error during setup: {e}")
        return False

def load_template_test():
    """Test loading HTML template"""
    print("\nTesting HTML template loading...")
    try:
        with open('src/newsletter_gen/config/newsletter_template.html', 'r') as file:
            template = file.read()
        print(f"✓ Template loaded successfully ({len(template)} characters)")
        return True
    except Exception as e:
        print(f"✗ Error loading template: {e}")
        return False

if __name__ == "__main__":
    print("🚀 NewsLetterGen Test Suite")
    print("=" * 50)
    
    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    success = test_basic_setup()
    success &= load_template_test()
    
    if success:
        print("\n🎉 All tests passed! The system is ready to use.")
        print("\nTo run the newsletter generation:")
        print("1. Streamlit GUI: poetry run streamlit run src/gui/app.py")
        print("2. Command line: poetry run newsletter_gen")
    else:
        print("\n❌ Some tests failed. Please check the configuration.")
