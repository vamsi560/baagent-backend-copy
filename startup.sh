#!/bin/bash
# Azure Web App startup script

echo "Starting BA Agent Backend on Azure Web App..."

# Get the port from Azure (Azure sets PORT environment variable)
PORT="${PORT:-5000}"

# Use gunicorn for production deployment
if command -v gunicorn &> /dev/null; then
    echo "Starting with Gunicorn on port $PORT..."
    gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120 --access-logfile - --error-logfile - --log-level info main:app
else
    echo "Gunicorn not found, starting with Flask development server..."
    python main.py
fi


