import os
import sys

# Ensure root and backend directories are in Python path
root_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(root_dir, "backend")

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from backend.app import app

# Expose app for WSGI / Vercel Serverless Function
application = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
