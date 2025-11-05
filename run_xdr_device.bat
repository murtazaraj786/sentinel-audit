@echo off
echo 📱 Running Defender XDR Audit with Device Code Login
echo ==================================================
echo.
echo You'll get a code to enter on another device.
echo Visit: https://microsoft.com/devicelogin
echo.
set AUTH_MODE=device
cd "Defender XDR Audit"
python defender_xdr_audit.py
pause