# 這個腳本用於更改 Windsurf 捷徑的圖示
# 動態取得當前使用者名稱
$currentUser = $env:USERNAME

# 目標捷徑路徑
$shortcutPath = "C:\Users\$currentUser\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Windsurf\Windsurf.lnk"
# 新圖示路徑
$iconPath = Join-Path $PSScriptRoot "resources\windsurf_old_150x150.ico"

# 檢查捷徑是否存在
if (-not (Test-Path $shortcutPath)) {
    Write-Host "錯誤: 找不到捷徑檔案 '$shortcutPath'"
    exit 1
}

# 檢查圖示檔案是否存在
if (-not (Test-Path $iconPath)) {
    Write-Host "錯誤: 找不到圖示檔案 '$iconPath'"
    exit 1
}

try {
    # 建立 WScript.Shell 物件以操作捷徑
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    
    # 儲存原始圖示路徑以便顯示
    $originalIcon = $shortcut.IconLocation
    
    # 設定新圖示
    $shortcut.IconLocation = $iconPath
    
    # 儲存變更
    $shortcut.Save()
    
    Write-Host "成功更改捷徑圖示"
    Write-Host "原始圖示: $originalIcon"
    Write-Host "新圖示: $iconPath"
    
} catch {
    Write-Host "錯誤: 無法更改捷徑圖示: $_"
    exit 1
} finally {
    # 釋放 COM 物件
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($shortcut) | Out-Null
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($shell) | Out-Null
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}
