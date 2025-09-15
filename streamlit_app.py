#!/usr/bin/env python3
"""
Streamlit App Entry Point for NewsLetterGen
Simplified version for Streamlit Cloud deployment
"""

import streamlit as st
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Try to import the full app
    from gui.app import NewsletterGenUI
    
    # Check if we have the required API keys
    if not st.secrets.get("GOOGLE_API_KEY") or not st.secrets.get("EXA_API_KEY"):
        st.error("⚠️ **API Keys Missing!**")
        st.markdown("""
        Please add your API keys in the Streamlit Cloud secrets:
        
        ```toml
        GOOGLE_API_KEY = "your-gemini-api-key"
        EXA_API_KEY = "your-exa-api-key"
        ```
        """)
        st.stop()
    
    # Set environment variables from secrets
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
    os.environ["EXA_API_KEY"] = st.secrets["EXA_API_KEY"]
    
    # Run the full app
    app = NewsletterGenUI()
    app.render()
    
except ImportError as e:
    # Fallback minimal app if imports fail
    st.title("📰 Newsletter Generator")
    st.error(f"**Import Error:** {str(e)}")
    st.markdown("""
    ## Dependency Issue
    
    There seems to be an issue with the dependencies. Please check:
    
    1. **Requirements.txt** - All dependencies are properly specified
    2. **API Keys** - Set in Streamlit Cloud secrets
    3. **Python Version** - Compatible with all packages
    
    ### Expected API Keys:
    - `GOOGLE_API_KEY` - For Gemini AI
    - `EXA_API_KEY` - For web research
    """)
    
    # Show system info for debugging
    with st.expander("🔍 System Information"):
        st.code(f"""
Python Version: {sys.version}
Current Directory: {os.getcwd()}
Python Path: {sys.path[:3]}...
Environment Keys: {list(os.environ.keys())[:10]}...
        """)

except Exception as e:
    # General error handler
    st.title("📰 Newsletter Generator")
    st.error(f"**Unexpected Error:** {str(e)}")
    st.markdown("Please check the deployment logs for more details.")
