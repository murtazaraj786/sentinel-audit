@echo off
echo 🌐 Running Defender XDR Audit with Interactive Browser Login
echo =========================================================
echo.
echo This will open a browser window for authentication.
echo.
set AUTH_MODE=browser
cd "Defender XDR Audit"
python defender_xdr_audit.py
pause