#!/bin/bash
# Render startup script for Newsletter Generation App

echo "🚀 Starting Newsletter Generation App on Render..."

# Set default port if not provided
export PORT=${PORT:-8501}

echo "📡 Port: $PORT"
echo "🔑 Environment variables loaded"

# Check if required environment variables are set
if [ -z "$EXA_API_KEY" ]; then
    echo "❌ Warning: EXA_API_KEY not set"
fi

if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Warning: GOOGLE_API_KEY not set"
fi

# Start Streamlit app
echo "🎯 Starting Streamlit on port $PORT..."
poetry run streamlit run src/gui/app.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false
