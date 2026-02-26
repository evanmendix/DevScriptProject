# 檢查管理員權限
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "請以系統管理員身分執行 (sudo powershell)！" -ForegroundColor Red
    exit
}

# 清除畫面，重新列出網卡
Clear-Host
Write-Host "=== 網路介面清單 ===" -ForegroundColor Cyan
$interfaces = Get-NetIPInterface -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.InterfaceAlias -notlike "*Virtual*" } | Sort-Object InterfaceIndex

foreach ($if in $interfaces) {
    $ipConfig = Get-NetIPConfiguration -InterfaceIndex $if.InterfaceIndex
    $ip = $ipConfig.IPv4Address.IPAddress
    $gw = $ipConfig.IPv4DefaultGateway.NextHop
    if (-not $gw) { $gw = "無 Gateway" }

    Write-Host "ID: [$($if.InterfaceIndex)] Name: $($if.InterfaceAlias)"
    Write-Host "    IP: $ip  |  Gateway: $gw" -ForegroundColor Gray
    Write-Host "--------------------------------------------------"
}

# === 使用者輸入 ===
Write-Host "請根據上方資訊輸入：" -ForegroundColor Yellow
$Internet_ID = Read-Host "1. 連接 [外網 Internet] 的介面 ID (例如 25)"
$VPN_ID      = Read-Host "2. 連接 [公司內網 VPN] 的介面 ID (例如 14)"

# === 防呆檢查 ===
if ($Internet_ID -eq $VPN_ID) {
    Write-Host "錯誤：Internet 和 VPN 不能是同一個介面！" -ForegroundColor Red
    exit
}

# 取得 VPN 網卡的詳細資訊
try {
    $VPNConfig = Get-NetIPConfiguration -InterfaceIndex $VPN_ID -ErrorAction Stop
    $VPNGateway = $VPNConfig.IPv4DefaultGateway.NextHop
    $VPNIP = $VPNConfig.IPv4Address.IPAddress
} catch {
    Write-Host "錯誤：找不到 ID 為 $VPN_ID 的網卡資訊，請確認輸入正確。" -ForegroundColor Red
    exit
}

# === 關鍵修正：檢查 Gateway 是否存在 ===
if ([string]::IsNullOrEmpty($VPNGateway)) {
    Write-Host "致命錯誤：VPN 網卡 (ID $VPN_ID) 目前沒有 Gateway！" -ForegroundColor Red
    Write-Host "原因可能是：Wi-Fi 未連線、或是該網路不提供 Gateway。"
    Write-Host "腳本無法繼續，因為無法設定路由。"
    exit
}

# === 關鍵修正：顯示即將執行的操作 ===
Write-Host "`n準備執行設定..." -ForegroundColor Cyan
Write-Host "外網優先介面: $Internet_ID (Metric 將設為 1)"
Write-Host "內網路由介面: $VPN_ID (IP: $VPNIP)"
Write-Host "目標 Gateway: $VPNGateway (將用於 10.252.1.3)"

# 簡單的網段檢查 (比對前三碼，非嚴謹但在這裡足夠防呆)
$GWSegment = $VPNGateway.Substring(0, $VPNGateway.LastIndexOf('.'))
$IPSegment = $VPNIP.Substring(0, $VPNIP.LastIndexOf('.'))

if ($GWSegment -ne $IPSegment) {
    Write-Host "`n[警告] VPN 網卡 IP ($VPNIP) 與 Gateway ($VPNGateway) 似乎不在同網段！" -ForegroundColor Magenta
    Write-Host "這可能會導致路由失敗。是否繼續？"
    $confirm = Read-Host "輸入 Y 繼續，其他鍵取消"
    if ($confirm -ne "Y") { exit }
}

# === 執行設定 ===
Write-Host "`n正在寫入設定..." -ForegroundColor Green

# 1. 重設 Metric (確保外網優先)
Set-NetIPInterface -InterfaceIndex $Internet_ID -InterfaceMetric 1
Set-NetIPInterface -InterfaceIndex $VPN_ID -InterfaceMetric 500

# 2. 清除舊路由
route delete 10.252.1.3 2> $null

# 3. 新增正確路由
# 使用 if 參數強制綁定介面，防止 Windows 自作聰明
route add 10.252.1.3 mask 255.255.255.255 $VPNGateway if $VPN_ID

# === 最終驗證 ===
Write-Host "`n設定完成。目前的路由表：" -ForegroundColor Cyan
route print 10.252.1.3

Write-Host "`n請檢查上方 Gateway Address 是否為 $VPNGateway" -ForegroundColor Yellow
pause