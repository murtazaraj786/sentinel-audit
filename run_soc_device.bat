@echo off
echo 📱 Running SOC Optimization Audit with Device Code Login
echo ======================================================
echo.
echo You'll get a code to enter on another device.
echo Visit: https://microsoft.com/devicelogin
echo.
set AUTH_MODE=device
cd "Sentinel SOC Optimisation Audit"
python soc_optimization_audit.py
pause