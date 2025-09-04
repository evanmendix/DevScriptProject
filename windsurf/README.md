# Windsurf 捷徑圖示更改工具

這個工具用於將 Windsurf 應用程式的捷徑圖示更改為自訂圖示（已內置於此專案）。

## 檔案說明

- `icon_switch.ps1`: PowerShell 腳本，負責實際更改捷徑的圖示
- `icon_switch.bat`: 批次檔，用於以管理員權限執行 PowerShell 腳本
- 內置圖示：`windsurf/resources/windsurf_old_150x150.ico`

## 使用方法

1. 確認 Windsurf 捷徑存在於：
   - `C:\Users\<你的使用者>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Windsurf\Windsurf.lnk`
2. 圖示檔已內置於此專案：`windsurf/resources/windsurf_old_150x150.ico`（腳本會自動以相對路徑讀取）
3. 以管理員身分點擊 `icon_switch.bat` 執行
4. 執行完成後，視窗會顯示原始與更新後的圖示路徑

## 注意事項

- 如果捷徑或圖示檔案不存在，腳本會顯示錯誤訊息
- 腳本會顯示原始圖示路徑和新圖示路徑
- 需要管理員權限才能修改系統捷徑
