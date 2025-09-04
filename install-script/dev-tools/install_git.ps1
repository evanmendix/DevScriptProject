# Self-elevate the script if required
if (-Not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] 'Administrator')) {
    Write-Output "Requesting administrator privileges..."
    $CommandLine = "-ExecutionPolicy Bypass -File `"" + $MyInvocation.MyCommand.Path + "`""
    Start-Process -FilePath PowerShell.exe -Verb RunAs -ArgumentList $CommandLine
    exit
}

# Check if Git is already installed
if (Get-Command git -ErrorAction SilentlyContinue) {
    $gitVersion = (git --version)
    Write-Output "Git is already installed on this system. No further action needed."
    Write-Output "Current version: $gitVersion"
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

# Install Git
try {
    Write-Output "Installing Git..."
    choco install git -y
    
    Write-Output "Git installed successfully!"
} catch {
    Write-Error "Git installation failed: $($_.Exception.Message)"
    Write-Output "`nPress any key to continue..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

# Refresh environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Verify Git installation
try {
    $gitVersion = (git --version)
    Write-Output "Git installation verified successfully."
    Write-Output "Installed version: $gitVersion"

    # Configure Git credentials helper
    Write-Output "`nConfiguring Git credential manager..."
    git config --system credential.helper manager-core

    Write-Output "Git credential manager configured."
} catch {
    Write-Error "Git verification failed. Please check your installation."
    Write-Output "`nPress any key to continue..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

Write-Output "`nInstallation complete! You can now use Git."
Write-Output "Remember to configure your Git user information:"
Write-Output "git config --global user.name `"Your Name`""
Write-Output "git config --global user.email `"your.email@example.com`""
Write-Output "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
