# Check if Scoop is already installed
if (Get-Command scoop -ErrorAction SilentlyContinue) {
    Write-Output "Scoop is already installed on this system. No further action needed."
    exit 0
}

# Set PowerShell execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Create Scoop installation directory
$scoopDir = "$env:USERPROFILE\scoop"
if (-not(Test-Path -Path $scoopDir)) {
    New-Item -ItemType Directory -Path $scoopDir | Out-Null
}

# Download and run Scoop installer
try {
    Invoke-RestMethod -Uri 'https://get.scoop.sh' | Invoke-Expression
    Write-Output "Scoop installed successfully!"
} catch {
    Write-Error "Scoop installation failed: $($_.Exception.Message)"
    exit 1
}

# Update PATH environment variable
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not($userPath -like "*$scoopDir\shims*")) {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$scoopDir\shims", "User")
    Write-Output "Environment variable updated"
}

Write-Output "Installation complete! Please restart PowerShell to use Scoop"
