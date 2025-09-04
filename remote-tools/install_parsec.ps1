# Self-elevate the script if required
if (-Not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] 'Administrator')) {
    Write-Output "Requesting administrator privileges..."
    $CommandLine = "-ExecutionPolicy Bypass -File `"" + $MyInvocation.MyCommand.Path + "`""
    Start-Process -FilePath PowerShell.exe -Verb RunAs -ArgumentList $CommandLine
    exit
}

# Check if Parsec is already installed
$parsecPath = "${env:ProgramFiles}\Parsec\parsecd.exe"
if (Test-Path $parsecPath) {
    Write-Output "Parsec is already installed on this system. No further action needed."
    Write-Output "`nPress any key to continue..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 0
}

# Check if Chocolatey is installed
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Error "Chocolatey is required but not installed. Please install Chocolatey first."
    Write-Output "`nPress any key to continue..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

# Install Parsec
try {
    Write-Output "Installing Parsec..."
    choco install parsec -y
    
    Write-Output "Parsec installed successfully!"
} catch {
    Write-Error "Parsec installation failed: $($_.Exception.Message)"
    Write-Output "`nPress any key to continue..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

Write-Output "`nInstallation complete!"
Write-Output "Please note:"
Write-Output "1. You need to create a Parsec account to use the service"
Write-Output "2. Make sure to configure your firewall settings if needed"
Write-Output "3. For optimal performance, use a wired network connection"
Write-Output "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
