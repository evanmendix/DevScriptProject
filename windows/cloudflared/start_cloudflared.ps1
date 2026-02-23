# --- 自動要求管理員權限 ---
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "需要管理員權限來執行此腳本，正在嘗試以管理員身分重新啟動..."
    Start-Process powershell.exe -Verb RunAs -ArgumentList "-File `"$($MyInvocation.MyCommand.Path)`""
    exit
}

# --- 腳本主要邏輯 ---
try {
    Write-Host "正在啟動 Cloudflared 服務..."
    Start-Service -Name cloudflared -ErrorAction Stop
    Write-Host "Cloudflared 服務已成功啟動。" -ForegroundColor Green
}
catch {
    Write-Host "啟動服務時發生錯誤：" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}
Read-Host -Prompt "按 Enter 鍵結束"