#!/bin/bash

# Get the port from Railway's PORT environment variable, default to 8000
PORT=${PORT:-8000}

echo "Starting TrinityAI on port $PORT"
echo "Health check will be available at http://0.0.0.0:$PORT/health"

# Start Gunicorn with the correct port
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --worker-class sync wsgi:application
