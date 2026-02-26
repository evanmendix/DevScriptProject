@echo off
chcp 65001 > nul

pushd "%~dp0"
cd ..\..\
set "PROJECT_ROOT=%CD%"

set "VBS_LAUNCHER=%~dp0script_launcher.vbs"
if not exist "%VBS_LAUNCHER%" (
    echo 錯誤：找不到啟動器 %VBS_LAUNCHER%
    pause
    popd
    exit /b 1
)

REM 使用 wscript 隱藏啟動，避免任何 console 視窗
wscript "%VBS_LAUNCHER%"
popd
