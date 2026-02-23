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

### develope/ide - IDE 開發工具
- **auto_clicker** - 自動圖片識別點擊工具
  - `auto_click.py` - 主要的自動點擊腳本，支援圖片識別和自動點擊
  - `setup.bat` - 一鍵環境設定腳本
  - `README.md` - 詳細使用說明文件
  - `requirements.txt` - Python 套件依賴
  - `target_images/` - 目標圖片存放目錄
- **windsurf** - Windsurf 應用程式工具
  - `icon_switch.bat` - 更改 Windsurf 捷徑圖示的工具
  - `icon_switch.ps1` - 圖示更改的 PowerShell 腳本

### install-script - 安裝腳本
- **dev-tools** - 開發工具安裝
  - Git、Java 17、Node.js (nvm)、Python、UV、VS Code 安裝腳本
- **package-managers** - 套件管理器
  - Chocolatey、Scoop 安裝腳本
- `install_all.ps1` - 一鍵安裝所有開發工具

### remote-tools - 遠端工具
- `install_parsec.ps1` - 安裝 Parsec 遠端桌面工具

### work-script - 工作相關腳本
- **cht** - 中華電信相關工具
  - `cht_proxy_toggle.bat` - 切換代理伺服器設定

### 其他工具
- `script_launcher.py` - 腳本啟動器 GUI 介面
- `scheduler.py` - 任務排程器

## 使用方式

### 1. 開發環境設定：
   - 執行 `install-script/install_all.ps1` 安裝所有開發工具
   - 或選擇性執行個別工具的安裝腳本

### 2. 自動點擊工具：
   ```bash
   # 基本使用
   uv run python develope/ide/auto_clicker/auto_click.py
   
   # 啟用滾輪功能
   uv run python develope/ide/auto_clicker/auto_click.py --scroll
   
   # 高信心度識別
   uv run python develope/ide/auto_clicker/auto_click.py --confidence 0.9
   
   # 測試模式（不實際點擊）
   uv run python develope/ide/auto_clicker/auto_click.py --test-mode
   ```

### 3. 系統管理：
   - 使用 `common_script` 下的工具管理螢幕設定、網路連線和系統更新

### 4. 遠端工作：
   - 安裝 Parsec 進行遠端桌面連線

## 環境需求

- Python 3.12+
- UV 套件管理器
- Windows 10/11

## 安裝依賴

```bash
# 安裝專案依賴
uv sync

# 或手動安裝自動點擊工具依賴
pip install pyautogui Pillow opencv-python
```

## 注意事項

- 部分腳本需要系統管理員權限才能執行
- 建議在執行腳本前先閱讀相關說明
- 某些功能可能需要特定的系統版本或環境
- 自動點擊工具使用前請先閱讀 `develope/ide/auto_clicker/README.md`

## 授權

此專案僅供個人使用，請勿用於商業用途。