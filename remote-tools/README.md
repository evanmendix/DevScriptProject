# 遠端工具安裝腳本

這個資料夾包含了遠端工作相關工具的安裝腳本。

## 可用的腳本

### install_parsec.ps1
- 安裝 Parsec 遠端桌面工具
- 使用 Chocolatey 進行安裝
- 會自動請求系統管理員權限
- 安裝完成後提供設定提醒：
  - 建立 Parsec 帳號
  - 防火牆設定
  - 網路連線建議

## 使用方式

這些腳本都可以直接點擊執行，或是在 PowerShell 中執行。例如：

```powershell
.\install_parsec.ps1
```

## 相依性需求

所有安裝腳本都需要 Chocolatey 套件管理工具：

1. 請先執行 `..\package-managers\install_chocolatey.ps1` 安裝 Chocolatey

## 注意事項

1. 所有腳本都會自動檢查是否已安裝，避免重複安裝
2. 所有腳本都會自動請求系統管理員權限
3. 安裝完成後可能需要額外的設定步驟
