@echo off
if not "%~1"=="HIDDEN" (
    powershell -windowstyle hidden -Command "Start-Process '%~dpnx0' -ArgumentList HIDDEN -WindowStyle Hidden"
    exit
)

setlocal enabledelayedexpansion

:check_loop
REM Check if Wi-Fi2 interface exists and is connected to ORBI
powershell -Command "Get-NetAdapter | Where-Object {$_.Name -eq 'Wi-Fi 2'} | Get-NetConnectionProfile" | findstr "ORBI" > nul
if !errorlevel! neq 0 (
    REM Not connected to ORBI, try to connect
    netsh wlan connect name=ORBI interface="Wi-Fi 3" > nul
    timeout /t 10 /nobreak > nul
)

timeout /t 3600 /nobreak > nul
goto check_loop
