"""
Root entrypoint for Vercel Flask deployment and local execution.
Bridges root execution into the backend/ modules.
"""
import os
import sys

# Add backend directory to sys.path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[INFO] Starting Fashion Forecasting Server on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
