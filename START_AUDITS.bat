@echo off
cls
echo.
echo 🛡️  SENTINEL AUDIT TOOLS - AUTHENTICATION MENU
echo =============================================
echo.
echo Choose how you want to authenticate:
echo.
echo 🌐 INTERACTIVE BROWSER LOGIN (opens browser window):
echo   1. Sentinel Audit + Browser Login
echo   2. SOC Optimization Audit + Browser Login  
echo   3. Defender XDR Audit + Browser Login
echo.
echo 📱 DEVICE CODE LOGIN (code for another device):
echo   4. Sentinel Audit + Device Code
echo   5. SOC Optimization Audit + Device Code
echo   6. Defender XDR Audit + Device Code
echo.
echo 🚀 ADVANCED OPTIONS:
echo   7. Interactive Authentication Helper (Python)
echo   8. Run All Audits (prompts for auth method)
echo.
echo   0. Exit
echo.
set /p choice="Enter your choice (0-8): "

if "%choice%"=="1" (
    call run_sentinel_browser.bat
) else if "%choice%"=="2" (
    call run_soc_browser.bat
) else if "%choice%"=="3" (
    call run_xdr_browser.bat
) else if "%choice%"=="4" (
    call run_sentinel_device.bat
) else if "%choice%"=="5" (
    call run_soc_device.bat
) else if "%choice%"=="6" (
    call run_xdr_device.bat
) else if "%choice%"=="7" (
    python run_with_auth.py
    pause
) else if "%choice%"=="8" (
    echo.
    echo 🚀 Running all available audit scripts...
    echo Each script will prompt for authentication method.
    echo.
    pause
    echo.
    echo Running Sentinel Audit...
    cd "Sentinel Audit"
    python sentinel_audit.py
    cd ..
    echo.
    echo Running SOC Optimization Audit...
    cd "Sentinel SOC Optimisation Audit"
    python soc_optimization_audit.py
    cd ..
    echo.
    echo Running Defender XDR Audit...
    cd "Defender XDR Audit"
    python defender_xdr_audit.py
    cd ..
    echo.
    echo ✅ All audits completed!
    pause
) else if "%choice%"=="0" (
    echo 👋 Goodbye!
    exit /b 0
) else (
    echo.
    echo ❌ Invalid choice. Please try again.
    pause
    goto :eof
)

echo.
echo 👋 Done! Check the audit folders for your CSV exports.
pause