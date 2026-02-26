@echo off
setlocal enabledelayedexpansion

echo ========================================
echo WiFi3 ORBI Auto-Check Removal Script
echo ========================================
echo.

REM Get startup folder and shortcut path
set "startup_folder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "shortcut_path=%startup_folder%\Check_WiFi3_ORBI.vbs"

echo Checking for existing startup script...
echo Shortcut path: %shortcut_path%
echo.

REM Stop any running check_wifi2.bat processes
echo Stopping any running WiFi3 check processes...
taskkill /f /im cmd.exe /fi "WINDOWTITLE eq Administrator: C:\WINDOWS\system32\cmd.exe - check_wifi.bat" 2>nul
taskkill /f /im powershell.exe /fi "COMMANDLINE eq *check_wifi.bat*" 2>nul

REM Also try to kill processes by image name that might be running the script
wmic process where "CommandLine like '%%check_wifi.bat%%'" delete 2>nul

echo Process termination attempted.
echo.

REM Remove the VBS startup script
if exist "%shortcut_path%" (
    echo Found startup script. Removing...
    del "%shortcut_path%" 2>nul
    if not exist "%shortcut_path%" (
        echo ✓ Startup script removed successfully.
    ) else (
        echo ✗ Failed to remove startup script. Please check permissions.
        exit /b 1
    )
) else (
    echo ℹ No startup script found. Nothing to remove.
)

echo.
echo ========================================
echo Removal completed successfully!
echo ========================================
echo.
echo The WiFi3 ORBI auto-check feature has been disabled.
echo - Background monitoring process stopped
echo - Startup script removed
echo.
echo If you want to re-enable it later, run setup_wifi_autorun.bat
echo.
pause
