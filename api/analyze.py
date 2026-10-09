import os
import sys

# Ensure root and backend directories are in Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
backend_dir = os.path.join(root_dir, "backend")

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from backend.app import app

def handler(environ, start_response):
    path = environ.get("PATH_INFO", "")
    if path == "/" or not path or path == "/api" or path == "/analyze":
        environ["PATH_INFO"] = "/api/analyze"
    return app(environ, start_response)

# Also expose app directly for WSGI environments
application = app
