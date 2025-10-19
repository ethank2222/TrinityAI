#!/usr/bin/env python3
"""
WSGI entry point for TrinityAI application.
This file is used by Gunicorn in production.
"""

import os
from app import app

if __name__ == "__main__":
    # This is for development only
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
else:
    # This is for production (Gunicorn)
    application = app
