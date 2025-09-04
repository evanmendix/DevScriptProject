# Script Launcher 設定指南

這個 GUI 應用程式提供了一個簡單的介面來執行 Windows 系統工具腳本。

## 環境需求

- Python 3.13
- UV 套件管理器

## 安裝步驟

1. 確保已安裝 UV：
   ```powershell
   # 如果尚未安裝 UV，請執行：
   curl -LsSf https://astral.sh/uv/install.ps1 | powershell
   ```

2. 建立並啟動虛擬環境：
   ```powershell
   uv venv
   .venv/Scripts/activate
   ```

3. 安裝相依套件：
   ```powershell
   uv pip install -e .
   ```

## 執行應用程式

1. 啟動虛擬環境（如果尚未啟動）：
   ```powershell
   .venv/Scripts/activate
   ```

2. 執行應用程式：
   ```powershell
   python script_launcher.py
   ```

## 功能說明

- 應用程式會自動掃描 `windows` 目錄下的所有腳本
- 腳本按照資料夾分類顯示在不同分頁中
- 滑鼠懸停在按鈕上會顯示腳本說明（從 README.md 中讀取）
- 點擊按鈕會以系統管理員權限執行對應的腳本
- 支援系統深色/淺色模式

## 注意事項

- 執行腳本時會要求系統管理員權限
- 確保所有腳本都在正確的目錄結構中
- 建議在 README.md 中維護完整的腳本說明
