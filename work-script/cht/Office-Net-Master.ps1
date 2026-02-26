# 1. 管理員權限檢查
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "請以系統管理員身分執行！" -ForegroundColor Red ; exit
}

Write-Host "=== 辦公室三網共存環境設定 (V9) ===" -ForegroundColor Cyan

# 2. 強力清理：移除會導致斷網的「鎖死預設路由」
# 解決您提到的：拔掉乙太網後 Wi-Fi 失效的問題
$ZombieGateway = "10.12.208.254"
route delete 0.0.0.0 mask 0.0.0.0 $ZombieGateway 2> $null
Write-Host "-> 已清理鎖死的乙太網持續路由。" -ForegroundColor Gray

# 3. 自動定位三張網卡 (透過硬體名稱)
$Eth = Get-NetAdapter | Where-Object { $_.InterfaceDescription -like "*Realtek PCIe*" -and $_.Status -eq "Up" } | Select-Object -First 1
$WifiExt = Get-NetAdapter | Where-Object { $_.InterfaceDescription -like "*D-Link*" -and $_.Status -eq "Up" } | Select-Object -First 1
$WifiVpn = Get-NetAdapter | Where-Object { $_.InterfaceDescription -like "*Intel*AX210*" -and $_.Status -eq "Up" } | Select-Object -First 1

# 4. 設定優先權 (Metric)
Write-Host "`n[優先權調整]" -ForegroundColor Yellow
if ($Eth) {
    Set-NetIPInterface -InterfaceIndex $Eth.InterfaceIndex -InterfaceMetric 5
    Write-Host " -> 乙太網路：已設為最優先 (Metric 5)" -ForegroundColor Green
}
if ($WifiExt) {
    Set-NetIPInterface -InterfaceIndex $WifiExt.InterfaceIndex -InterfaceMetric 20
    Write-Host " -> WiFi 外網：已設為備援優先 (Metric 20)" -ForegroundColor Green
}
if ($WifiVpn) {
    Set-NetIPInterface -InterfaceIndex $WifiVpn.InterfaceIndex -InterfaceMetric 500
    Write-Host " -> WiFi VPN ：已設為最低優先 (Metric 500)" -ForegroundColor Green
}

# 5. 設定 VPN 登入頁持續路由 (核心修正)
# 使用 -p 參數，確保 Wi-Fi 閃斷或睡眠喚醒後，設定依然存在
if ($WifiVpn) {
    $TargetIP = "10.252.1.3"
    $VPNGateway = "10.0.1.253"
    route delete $TargetIP 2> $null
    route add $TargetIP mask 255.255.255.255 $VPNGateway if $WifiVpn.InterfaceIndex -p
    Write-Host "`n[路由鎖定]" -ForegroundColor Yellow
    Write-Host " -> 已將 $TargetIP 永久指向 WiFi 3 (Gateway: $VPNGateway)" -ForegroundColor Cyan
}

Write-Host "`n=== 設定完成！現狀說明 ===" -ForegroundColor Yellow
Write-Host "1. 插線時：自動走『乙太網』上網。"
Write-Host "2. 拔線時：自動切換至『WiFi 外網』。"
Write-Host "3. VPN 登入頁：無論有無插線，固定走『WiFi VPN』。"
Write-Host "4. 注意：若乙太網需 Proxy，請記得在連線時開啟，切換回 WiFi 前關閉。"
pause