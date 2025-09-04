# Self-elevate the script if required
if (-Not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] 'Administrator')) {
    Write-Output "Requesting administrator privileges..."
    $CommandLine = "-ExecutionPolicy Bypass -File `"" + $MyInvocation.MyCommand.Path + "`""
    Start-Process -FilePath PowerShell.exe -Verb RunAs -ArgumentList $CommandLine
    exit
}

# Check if VS Code is already installed
if (Get-Command code -ErrorAction SilentlyContinue) {
    Write-Output "Visual Studio Code is already installed on this system. No further action needed."
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

# Install VS Code
try {
    Write-Output "Installing Visual Studio Code..."
    choco install vscode -y
    
    Write-Output "Visual Studio Code installed successfully!"
} catch {
    Write-Error "Visual Studio Code installation failed: $($_.Exception.Message)"
    Write-Output "`nPress any key to continue..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

# Refresh environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Install common VS Code extensions
try {
    Write-Output "`nInstalling common VS Code extensions..."
    
    # Programming language support
    code --install-extension ms-python.python
    code --install-extension vscjava.vscode-java-pack
    code --install-extension dbaeumer.vscode-eslint
    code --install-extension esbenp.prettier-vscode
    
    # Git integration
    code --install-extension eamodio.gitlens
    
    # Docker support
    code --install-extension ms-azuretools.vscode-docker
    
    Write-Output "VS Code extensions installed successfully!"
} catch {
    Write-Warning "Some extensions might have failed to install. You can install them manually from VS Code."
}

Write-Output "`nInstallation complete! You can now use Visual Studio Code."
Write-Output "Common VS Code commands:"
Write-Output "- code .          : Open VS Code in current directory"
Write-Output "- code <file>     : Open a specific file"
Write-Output "- code --list-extensions : List installed extensions"
Write-Output "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
