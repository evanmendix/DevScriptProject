# Self-elevate the script if required
if (-Not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] 'Administrator')) {
    Write-Output "Requesting administrator privileges..."
    $CommandLine = "-ExecutionPolicy Bypass -File `"" + $MyInvocation.MyCommand.Path + "`""
    Start-Process -FilePath PowerShell.exe -Verb RunAs -ArgumentList $CommandLine
    exit
}

# Check if NVM is already installed
if (Get-Command nvm -ErrorAction SilentlyContinue) {
    Write-Output "NVM is already installed on this system. No further action needed."
    Write-Output "Current NVM version: $(nvm version)"
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

# Install NVM for Windows
try {
    Write-Output "Installing NVM for Windows..."
    choco install nvm -y
    
    Write-Output "NVM installed successfully!"
} catch {
    Write-Error "NVM installation failed: $($_.Exception.Message)"
    Write-Output "`nPress any key to continue..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

# Refresh environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Verify NVM installation
try {
    $nvmVersion = nvm version
    Write-Output "NVM installation verified successfully."
    Write-Output "Installed version: $nvmVersion"

    # Install latest LTS version of Node.js
    Write-Output "`nInstalling latest LTS version of Node.js..."
    nvm install lts
    nvm use lts

    # Verify Node.js installation
    $nodeVersion = node -v
    $npmVersion = npm -v
    Write-Output "Node.js installation complete!"
    Write-Output "Node.js version: $nodeVersion"
    Write-Output "NPM version: $npmVersion"
} catch {
    Write-Error "NVM verification failed. Please check your installation."
    Write-Output "`nPress any key to continue..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

Write-Output "`nInstallation complete! You can now use NVM to manage Node.js versions."
Write-Output "Common NVM commands:"
Write-Output "- nvm list        : List installed Node.js versions"
Write-Output "- nvm install lts : Install latest LTS version"
Write-Output "- nvm use <version> : Switch to specific version"
Write-Output "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
