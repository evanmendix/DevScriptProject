# MyPersonalEnvironmentScript

這是一個個人環境設定和工具腳本的集合，用於快速設定和管理 Windows 系統環境。

## 專案結構和功能

### common_script - 通用腳本
- **internet** - 網路相關工具
  - `check_wifi2.bat` - WiFi 連線狀態檢查
  - `setup_wifi2_autorun.bat` - 設定 WiFi 檢查自動執行
- **screen_control** - 螢幕控制工具
  - `screen_extend.bat` - 設定延伸螢幕
  - `screen_internal.bat` - 切換至內部螢幕
  - `screen_mirror.bat` - 設定螢幕鏡像
- **windows_update** - Windows Update 控制
  - `stop_update.bat` - 停用 Windows Update
  - `freset_update.bat` - 重設 Windows Update 設定

### install-script - 安裝腳本
- **dev-tools** - 開發工具安裝
  - Git、Java 17、Node.js (nvm)、Python、UV、VS Code 安裝腳本
- **package-managers** - 套件管理器
  - Chocolatey、Scoop 安裝腳本
- `install_all.ps1` - 一鍵安裝所有開發工具

### remote-tools - 遠端工具
- `install_parsec.ps1` - 安裝 Parsec 遠端桌面工具

### windsurf - Windsurf 應用程式工具
- `icon_switch.bat` - 更改 Windsurf 捷徑圖示的工具
- `icon_switch.ps1` - 圖示更改的 PowerShell 腳本

### work-script - 工作相關腳本
- **cht** - 中華電信相關工具
  - `cht_proxy_toggle.bat` - 切換代理伺服器設定

## 使用方式

1. 開發環境設定：
   - 執行 `install-script/install_all.ps1` 安裝所有開發工具
   - 或選擇性執行個別工具的安裝腳本

2. 系統管理：
   - 使用 `common_script` 下的工具管理螢幕設定、網路連線和系統更新

3. 遠端工作：
   - 安裝 Parsec 進行遠端桌面連線

## 注意事項

- 部分腳本需要系統管理員權限才能執行
- 建議在執行腳本前先閱讀相關說明
- 某些功能可能需要特定的系統版本或環境