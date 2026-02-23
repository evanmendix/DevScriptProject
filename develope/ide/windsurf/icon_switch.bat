@echo off
REM This script changes the icon of the Windsurf shortcut
REM It runs the PowerShell script with administrative privileges

powershell.exe -ExecutionPolicy Bypass -Command "Start-Process powershell.exe -ArgumentList '-ExecutionPolicy Bypass -File "%~dp0icon_switch.ps1"' -Verb RunAs"

pause