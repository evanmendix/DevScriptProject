@echo off
setlocal enabledelayedexpansion

REM Get script locations
set "startup_folder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "shortcut_path=%startup_folder%\Check_WiFi3_ORBI.vbs"
echo Shortcut path: %shortcut_path%
set "script_path=%~dp0check_wifi.bat"

REM Create VBS script
(
echo Set shell = CreateObject^("WScript.Shell"^)
echo shell.Run "powershell -windowstyle hidden -Command Start-Process '%script_path%' -ArgumentList HIDDEN -WindowStyle Hidden", 0, false
) > "%shortcut_path%"

if exist "%shortcut_path%" (
    echo Setup completed successfully.
    echo The script will run in background without window.
    echo Script location: %script_path%
) else (
    echo Error: Failed to create startup script.
    exit /b 1
)
