# Self-elevate the script if required
if (-Not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] 'Administrator')) {
    Write-Output "Requesting administrator privileges..."
    $CommandLine = "-ExecutionPolicy Bypass -File `"" + $MyInvocation.MyCommand.Path + "`""
    Start-Process -FilePath PowerShell.exe -Verb RunAs -ArgumentList $CommandLine
    exit
}

# Check if Java 17 is already installed
$javaVersion = $null
try {
    $javaVersion = (cmd /c "java -version 2>&1") | Out-String
    if ($javaVersion -match "version `"17\.") {
        Write-Output "Java 17 is already installed on this system. No further action needed."
        Write-Output "Current Java version: $($javaVersion.Trim())"
        Write-Output "`nPress any key to continue..."
        $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
        exit 0
    }
} catch {
    # Java is not installed or not in PATH
}

# Check if Chocolatey is installed
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Error "Chocolatey is required but not installed. Please install Chocolatey first."
    Write-Output "`nPress any key to continue..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

# Install OpenJDK 17
try {
    Write-Output "Installing OpenJDK 17..."
    choco install openjdk17 -y
    
    Write-Output "Java 17 installed successfully!"
} catch {
    Write-Error "Java 17 installation failed: $($_.Exception.Message)"
    Write-Output "`nPress any key to continue..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

# Verify installation and environment variables
$javaHome = [Environment]::GetEnvironmentVariable("JAVA_HOME", "Machine")

# Verify Java command
try {
    $newJavaVersion = (cmd /c "java -version 2>&1") | Out-String
    if ($newJavaVersion -match "version `"17\.") {
        Write-Output "Java 17 installation verified successfully."
        Write-Output "Installed version: $($newJavaVersion.Trim())"
    } else {
        Write-Warning "Java is installed but version verification failed. Expected version 17, but got: $($newJavaVersion.Trim())"
    }
} catch {
    Write-Error "Java command verification failed. Please check your installation."
    Write-Output "`nPress any key to continue..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

# Verify JAVA_HOME
if ([string]::IsNullOrEmpty($javaHome)) {
    Write-Warning "JAVA_HOME environment variable is not set."
} else {
    Write-Output "JAVA_HOME is set to: $javaHome"
}

Write-Output "Installation complete! You can now use Java 17."
Write-Output "Note: You may need to restart your PowerShell session to use Java commands."
Write-Output "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
