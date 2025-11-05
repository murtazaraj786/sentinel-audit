@echo off
echo 🌐 Running SOC Optimization Audit with Interactive Browser Login
echo =============================================================
echo.
echo This will open a browser window for authentication.
echo.
set AUTH_MODE=browser
cd "Sentinel SOC Optimisation Audit"
python soc_optimization_audit.py
pause