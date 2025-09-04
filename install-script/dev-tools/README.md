# 開發工具安裝腳本

這個資料夾包含了各種開發工具的安裝腳本。所有腳本都會先檢查是否已安裝，避免重複安裝的問題。

## 可用的腳本

### install_java17.ps1
- 安裝 OpenJDK 17
- 使用 Chocolatey 進行安裝
- 會自動請求系統管理員權限
- 自動設定 JAVA_HOME 環境變數

### install_nvm.ps1
- 安裝 NVM (Node Version Manager) for Windows
- 使用 Chocolatey 進行安裝
- 會自動請求系統管理員權限
- 安裝完成後會自動安裝最新的 Node.js LTS 版本
- 包含常用指令說明

### install_git.ps1
- 安裝 Git 版本控制系統
- 使用 Chocolatey 進行安裝
- 會自動請求系統管理員權限
- 自動設定 Git 認證管理員
- 安裝完成後提供設定使用者資訊的指引

### install_python.ps1
- 安裝最新版本的 Python
- 使用 Chocolatey 進行安裝
- 會自動請求系統管理員權限
- 自動更新 pip 到最新版本
- 安裝 virtualenv 套件方便管理虛擬環境
- 包含常用指令說明

### install_vscode.ps1
- 安裝 Visual Studio Code
- 使用 Chocolatey 進行安裝
- 會自動請求系統管理員權限
- 自動安裝常用擴充套件：
  - Python 支援
  - Java 開發包
  - ESLint 和 Prettier
  - GitLens
  - Docker 支援
- 包含常用指令說明

### install_uv.ps1
- 安裝 UV Python 套件管理工具
- 使用 Scoop 進行安裝
- 會自動檢查 Scoop 是否已安裝
- 提供更快速的 Python 套件安裝體驗
- 支援與 pip 相容的指令
- 包含安裝驗證和版本資訊顯示

### install_docker.ps1
- 安裝 Docker Desktop for Windows
- 使用 Chocolatey 進行安裝
- 會自動請求系統管理員權限
- 自動檢查並安裝必要的系統需求：
  - Windows 10 版本 2004 (Build 19041) 或更新版本
  - WSL 2 (Windows Subsystem for Linux)
- 包含常用指令說明
- 安裝完成後需要重新啟動電腦

## 使用方式

這些腳本都可以直接點擊執行，或是在 PowerShell 中執行。例如：

```powershell
.\install_java17.ps1
.\install_nvm.ps1
.\install_git.ps1
.\install_python.ps1
.\install_vscode.ps1
.\install_uv.ps1
.\install_docker.ps1
```

## 相依性需求

所有安裝腳本都需要 Chocolatey 套件管理工具：

1. 請先執行 `..\package-managers\install_chocolatey.ps1` 安裝 Chocolatey

## 注意事項

1. 所有腳本都會自動檢查是否已安裝，避免重複安裝
2. 所有腳本都會自動請求系統管理員權限
3. 安裝完成後可能需要重新開啟 PowerShell 視窗才能使用新安裝的工具
4. Docker Desktop 安裝後需要重新啟動電腦
5. 部分工具可能需要額外的系統需求：
   - Docker Desktop 需要 Windows 10 版本 2004 或更新版本
   - Docker Desktop 需要 WSL 2
