# Self-elevate the script if required
if (-Not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] 'Administrator')) {
    Write-Output "Requesting administrator privileges..."
    $CommandLine = "-ExecutionPolicy Bypass -File `"" + $MyInvocation.MyCommand.Path + "`""
    Start-Process -FilePath PowerShell.exe -Verb RunAs -ArgumentList $CommandLine
    exit
}

# Install Chocolatey
Write-Output "Installing Chocolatey..."
& "${PSScriptRoot}\package-managers\install_chocolatey.ps1"

# Install Scoop
Write-Output "Installing Scoop..."
& "${PSScriptRoot}\package-managers\install_scoop.ps1"

# Install Java 17
Write-Output "Installing Java 17..."
& "${PSScriptRoot}\dev-tools\install_java17.ps1"

# Install Git
Write-Output "Installing Git..."
& "${PSScriptRoot}\dev-tools\install_git.ps1"

# Install NVM
Write-Output "Installing NVM..."
& "${PSScriptRoot}\dev-tools\install_nvm.ps1"

# Install Python
Write-Output "Installing Python..."
& "${PSScriptRoot}\dev-tools\install_python.ps1"

# Install UV
Write-Output "Installing UV..."
& "${PSScriptRoot}\dev-tools\install_uv.ps1"

# Install VSCode
Write-Output "Installing Visual Studio Code..."
& "${PSScriptRoot}\dev-tools\install_vscode.ps1"

Write-Output "All installations are complete!"
