<#
.SYNOPSIS
    Toggles the system-wide proxy settings and user environment variables for development tools.
#>
param(
    [string]$ProxyServer = "http://10.160.3.88:8080"
)

# Registry path for Internet Settings
$RegPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings"

# Get current proxy state from registry
$ProxyEnabled = Get-ItemProperty -Path $RegPath -Name ProxyEnable -ErrorAction SilentlyContinue

if ($ProxyEnabled -and $ProxyEnabled.ProxyEnable -eq 1) {
    # --- DISABLE PROXY ---
    Write-Host "Currently Enabled. Disabling System Proxy..." -ForegroundColor Yellow

    # 1. Disable system proxy in registry
    Set-ItemProperty -Path $RegPath -Name "ProxyEnable" -Value 0

    # 2. Remove user environment variables
    [Environment]::SetEnvironmentVariable("HTTP_PROXY", $null, "User")
    [Environment]::SetEnvironmentVariable("HTTPS_PROXY", $null, "User")

    Write-Host "System Proxy and Environment Variables have been DISABLED." -ForegroundColor Green
    Write-Host "Please RESTART any open terminals or applications to apply changes." -ForegroundColor Cyan

} else {
    # --- ENABLE PROXY ---
    Write-Host "Currently Disabled. Enabling System Proxy..." -ForegroundColor Yellow

    # 1. Enable system proxy and set server in registry
    Set-ItemProperty -Path $RegPath -Name "ProxyEnable" -Value 1
    Set-ItemProperty -Path $RegPath -Name "ProxyServer" -Value $ProxyServer.Replace("http://", "") # Registry doesn't need http://

    # 2. Set user environment variables
    [Environment]::SetEnvironmentVariable("HTTP_PROXY", $ProxyServer, "User")
    [Environment]::SetEnvironmentVariable("HTTPS_PROXY", $ProxyServer, "User")

    Write-Host "System Proxy and Environment Variables have been ENABLED." -ForegroundColor Green
    Write-Host "Please RESTART any open terminals or applications to apply changes." -ForegroundColor Cyan
}

# You can add a pause here if running from file explorer
# Read-Host "Press Enter to exit..."