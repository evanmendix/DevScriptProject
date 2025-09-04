# Check if Chocolatey is already installed
if (Get-Command choco -ErrorAction SilentlyContinue) {
    Write-Output "Chocolatey is already installed on this system. No further action needed."
    exit 0
}

# Ensure we're running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Error "This script requires administrator privileges. Please run PowerShell as administrator."
    exit 1
}

# Set execution policy
Set-ExecutionPolicy Bypass -Scope Process -Force

try {
    # Install Chocolatey
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    
    Write-Output "Chocolatey installed successfully!"
} catch {
    Write-Error "Chocolatey installation failed: $($_.Exception.Message)"
    exit 1
}

# Verify installation and environment variables
$chocoPath = "C:\ProgramData\chocolatey\bin"
$systemPath = [Environment]::GetEnvironmentVariable("Path", "Machine")

# Verify Chocolatey command
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Error "Installation verification failed. Chocolatey command not found."
    exit 1
}

# Verify PATH environment variable
if (-not ($systemPath -like "*$chocoPath*")) {
    Write-Warning "Chocolatey bin path not found in system PATH. You may need to restart your PowerShell session."
} else {
    Write-Output "Chocolatey PATH verification successful."
}

Write-Output "Installation complete! You can now use Chocolatey with the 'choco' command."
Write-Output "Note: You may need to restart your PowerShell session to use Chocolatey commands."
