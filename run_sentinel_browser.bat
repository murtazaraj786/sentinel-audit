@echo off
echo 🌐 Running Sentinel Audit with Interactive Browser Login
echo =====================================================
echo.
echo This will open a browser window for authentication.
echo.
set AUTH_MODE=browser
cd "Sentinel Audit"
python sentinel_audit.py
pause