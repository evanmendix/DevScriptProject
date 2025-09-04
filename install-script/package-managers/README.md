# 套件管理工具安裝腳本

這個資料夾包含了套件管理工具的安裝腳本。所有腳本都會先檢查是否已安裝，避免重複安裝的問題。

## 可用的腳本

### install_scoop.ps1
- 安裝 Scoop（使用者層級的套件管理工具）
- 自動設定必要的環境變數
- 不需要系統管理員權限

### install_chocolatey.ps1
- 安裝 Chocolatey（系統層級的套件管理工具）
- 需要系統管理員權限執行
- 自動設定必要的環境變數

## 使用方式

這些腳本都可以直接點擊執行，或是在 PowerShell 中執行。例如：

```powershell
.\install_scoop.ps1
.\install_chocolatey.ps1
```

注意：
- `install_chocolatey.ps1` 需要系統管理員權限
