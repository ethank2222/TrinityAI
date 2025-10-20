#!/bin/bash

# Get the port from Railway's PORT environment variable, default to 8000
PORT=${PORT:-8000}

echo "Starting TrinityAI on port $PORT"
echo "Health check will be available at http://0.0.0.0:$PORT/health"

# Wait a moment for the application to fully start
sleep 2

# Start Gunicorn with the correct port and better error handling
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --worker-class sync --access-logfile - --error-logfile - --log-level info wsgi:application
