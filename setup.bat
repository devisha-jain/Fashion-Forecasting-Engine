@echo off
echo === Fashion Forecasting Lab - Windows Setup Script ===
echo.

echo [1/2] Installing Python backend dependencies...
venv\Scripts\pip.exe install -r backend\requirements.txt
echo [OK] Python dependencies verified!
echo.

echo [2/2] Installing Next.js frontend dependencies...
cd frontend
call npm install
cd ..
echo [OK] Frontend packages verified!
echo.

echo === SETUP COMPLETE ===
echo.
echo To run the application:
echo   Terminal 1 (Backend):  venv\Scripts\python.exe backend\app.py
echo   Terminal 2 (Frontend): cd frontend ^&^& npm run dev
echo.
echo Then open http://localhost:3000 in your browser.
pause
