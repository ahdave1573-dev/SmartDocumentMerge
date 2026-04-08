@echo off
echo ================================================
echo  Smart PDF Tools — Setup & Run
echo ================================================
echo.

echo [1/2] Installing Python dependencies...
python -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: pip install failed. Please check your internet connection.
    pause
    exit /b 1
)

echo.
echo [2/2] Starting Flask server...
echo.
echo ================================================
echo  APP IS RUNNING! 🚀
echo  Open your browser at: http://localhost:5000
echo ================================================
echo.
echo Press Ctrl+C in this window to stop the server.
echo.
python app.py

pause
