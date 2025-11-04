#!/bin/bash

# Neo RAG Chatbot Startup Script

echo "Starting Neo RAG Chatbot..."
echo ""
echo "Make sure you have set up your .env file with API keys!"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please create a .env file with your API keys."
    exit 1
fi

# Start the server
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo ""
echo "Server stopped."
