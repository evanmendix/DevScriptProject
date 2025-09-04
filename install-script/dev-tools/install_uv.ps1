# Install UV through scoop
# Reference: https://github.com/astral-sh/uv

$ErrorActionPreference = "Stop"

Write-Host "Installing UV through scoop..."

# Check if scoop is installed
if (!(Get-Command scoop -ErrorAction SilentlyContinue)) {
    Write-Error "Scoop is not installed. Please install scoop first."
    exit 1
}

# Install UV
scoop bucket add main
scoop install uv

# Verify installation and environment variables
if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Host "UV has been successfully installed!"
    Write-Host "Version: $(uv --version)"
    
    # Check if UV is in the PATH
    $uvPath = (Get-Command uv).Source
    Write-Host "UV is installed at: $uvPath"
    
    # Verify that the UV directory is in the user's PATH
    $uvDir = Split-Path -Parent $uvPath
    $userPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
    
    if ($userPath -split ";" -contains $uvDir) {
        Write-Host "UV directory is correctly set in user's PATH"
    } else {
        Write-Warning "UV directory is not in user's PATH. This might be because Scoop is still updating the environment."
        Write-Host "You may need to restart your PowerShell session to use UV."
    }
} else {
    Write-Error "Failed to install UV"
    exit 1
}
