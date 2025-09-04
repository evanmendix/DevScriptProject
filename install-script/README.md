# 安裝腳本集

此目錄是更大專案的一部分，旨在管理個人命令行工具和自動化腳本。`install-script` 目錄專門包含用於自動化安裝和配置開發工具的 PowerShell 腳本。

## 專案結構

```
install-script/
├── package-managers/     # 套件管理工具
│   ├── install_chocolatey.ps1   # Chocolatey 安裝腳本
│   ├── install_scoop.ps1        # Scoop 安裝腳本
│   └── README.md
│
├── dev-tools/           # 開發工具
│   ├── install_java17.ps1       # Java 開發環境
│   ├── install_nvm.ps1          # Node.js 版本管理
│   ├── install_git.ps1          # Git 版本控制
│   ├── install_python.ps1       # Python 開發環境
│   ├── install_vscode.ps1       # Visual Studio Code
│   ├── install_uv.ps1          # UV Python 套件管理工具
│   └── README.md
│
├── remote-tools/        # 遠端工具
│   ├── install_parsec.ps1       # Parsec 遠端桌面
│   └── README.md
│
└── install_all.ps1      # 批次安裝腳本
```

## 快速開始

1. 以系統管理員身分開啟 PowerShell
2. 執行批次安裝腳本：
   ```powershell
   .\install_all.ps1
   ```

## 個別安裝

如果你只想安裝特定工具，可以直接執行對應的腳本：

```powershell
# 安裝套件管理工具
.\package-managers\install_chocolatey.ps1
.\package-managers\install_scoop.ps1

# 安裝開發工具
.\dev-tools\install_java17.ps1
.\dev-tools\install_nvm.ps1
.\dev-tools\install_git.ps1
.\dev-tools\install_python.ps1
.\dev-tools\install_vscode.ps1
.\dev-tools\install_uv.ps1

# 安裝遠端工具
.\remote-tools\install_parsec.ps1
```

## 特色功能

1. **自動檢查**
   - 檢查是否已安裝
   - 檢查系統需求
   - 檢查相依性

2. **環境設定**
   - 自動設定環境變數
   - 自動更新 PATH
   - 自動安裝必要的擴充套件

3. **使用者體驗**
   - 中文介面
   - 清楚的安裝進度提示
   - 錯誤處理與提示
   - 需要時自動重新啟動

## 注意事項

1. 所有腳本都需要系統管理員權限
2. 某些工具安裝後需要重新啟動電腦
3. 批次安裝時會自動處理重新啟動的需求
4. 建議使用有線網路進行安裝
5. 安裝過程中請勿關閉 PowerShell 視窗

## 系統需求

- Windows 10 版本 2004 (Build 19041) 或更新版本
- PowerShell 5.1 或更新版本
- 網際網路連線
- 系統管理員權限
