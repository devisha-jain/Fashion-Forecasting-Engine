#!/bin/bash
echo "=== Fashion Forecasting Lab - Unix Setup Script ==="
echo ""

echo "[1/2] Installing Python backend dependencies..."
if [ -d "venv" ]; then
    ./venv/bin/pip install -r backend/requirements.txt
else
    pip install -r backend/requirements.txt
fi
echo "[OK] Python packages installed!"
echo ""

echo "[2/2] Installing Next.js frontend dependencies..."
cd frontend
npm install
cd ..
echo "[OK] Next.js packages installed!"
echo ""

echo "=== SETUP COMPLETE ==="
echo ""
echo "To run the services:"
echo "  Terminal 1: python -m flask --app backend/app.py run --port 5000"
echo "  Terminal 2: cd frontend && npm run dev"
echo ""
