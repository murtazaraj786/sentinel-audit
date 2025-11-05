@echo off
echo 📱 Running Sentinel Audit with Device Code Login
echo ==============================================
echo.
echo You'll get a code to enter on another device.
echo Visit: https://microsoft.com/devicelogin
echo.
set AUTH_MODE=device
cd "Sentinel Audit"
python sentinel_audit.py
pause