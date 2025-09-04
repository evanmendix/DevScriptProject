# Self-elevate the script if required
if (-Not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] 'Administrator')) {
    Write-Output "Requesting administrator privileges..."
    $CommandLine = "-ExecutionPolicy Bypass -File `"" + $MyInvocation.MyCommand.Path + "`""
    Start-Process -FilePath PowerShell.exe -Verb RunAs -ArgumentList $CommandLine
    exit
}

# Check if Python is already installed
$pythonVersion = $null
try {
    $pythonVersion = (python --version 2>&1)
    Write-Output "Python is already installed on this system. No further action needed."
    Write-Output "Current version: $pythonVersion"
    
    $pipVersion = (pip --version)
    Write-Output "pip version: $pipVersion"
    
    Write-Output "`nPress any key to continue..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 0
} catch {
    # Python is not installed or not in PATH
}

# Check if Chocolatey is installed
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Error "Chocolatey is required but not installed. Please install Chocolatey first."
    Write-Output "`nPress any key to continue..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

# Install Python
try {
    Write-Output "Installing Python..."
    # Install Python with pip and add to PATH
    choco install python -y
    
    Write-Output "Python installed successfully!"
} catch {
    Write-Error "Python installation failed: $($_.Exception.Message)"
    Write-Output "`nPress any key to continue..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

# Refresh environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Verify Python installation
try {
    $pythonVersion = (python --version 2>&1)
    Write-Output "Python installation verified successfully."
    Write-Output "Installed version: $pythonVersion"

    # Verify and upgrade pip
    Write-Output "`nUpgrading pip to latest version..."
    python -m pip install --upgrade pip
    $pipVersion = (pip --version)
    Write-Output "pip version: $pipVersion"

    # Install common development packages
    Write-Output "`nInstalling common Python development packages..."
    pip install virtualenv
    Write-Output "virtualenv installed for Python virtual environment management"
} catch {
    Write-Error "Python verification failed. Please check your installation."
    Write-Output "`nPress any key to continue..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

Write-Output "`nInstallation complete! You can now use Python and pip."
Write-Output "Common Python commands:"
Write-Output "- python --version : Check Python version"
Write-Output "- pip list        : List installed packages"
Write-Output "- virtualenv venv : Create a new virtual environment"
Write-Output "- python -m venv venv : Create a new virtual environment (built-in)"
Write-Output "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
