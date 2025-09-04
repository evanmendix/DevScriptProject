# Windows 系統工具腳本

這個目錄包含各種 Windows 系統相關的工具腳本，用於管理和控制 Windows 系統的各項功能。

## 目錄結構

### internet - 網路工具
- `check_wifi2.bat` - WiFi 連線狀態檢查工具
  - 功能：定期檢查 WiFi 連線狀態，如果斷線會自動重新連線
  - 使用方式：直接執行即可，建議搭配 `setup_wifi2_autorun.bat` 設定開機自動執行
- `setup_wifi2_autorun.bat` - 設定 WiFi 檢查自動執行
  - 功能：將 WiFi 檢查工具加入開機自動執行項目
  - 使用方式：以系統管理員權限執行

### screen_control - 螢幕控制
- `screen_extend.bat` - 設定延伸螢幕
  - 功能：將外接螢幕設定為延伸模式
  - 使用方式：連接外接螢幕後執行
- `screen_internal.bat` - 切換至內部螢幕
  - 功能：關閉外接螢幕，只使用筆電內建螢幕
  - 使用方式：想要切換回內建螢幕時執行
- `screen_mirror.bat` - 設定螢幕鏡像
  - 功能：將外接螢幕設定為鏡像模式
  - 使用方式：需要螢幕同步顯示時執行

### windows_update - Windows Update 控制
- `stop_update.bat` - 停用 Windows Update
  - 功能：透過修改 Registry 設定來停用 Windows Update
  - 使用方式：以系統管理員權限執行
- `reset_update.bat` - 重設 Windows Update 設定
  - 功能：移除停用設定，恢復 Windows Update 功能
  - 使用方式：以系統管理員權限執行

## 注意事項

1. 系統管理員權限
   - 大部分腳本需要系統管理員權限才能正常運作
   - 特別是修改系統設定的腳本（如 Windows Update 相關）

2. 執行環境
   - 這些腳本主要在 Windows 10 和 Windows 11 上測試
   - 某些功能在不同 Windows 版本上可能有差異

3. 安全性
   - 修改系統設定前建議先備份重要資料
   - 特別是修改 Registry 的操作要特別小心

4. 自動執行
   - 設定自動執行的腳本（如 WiFi 檢查）會在開機時自動啟動
   - 如果發現系統效能受影響，可以手動關閉或移除自動執行設定
