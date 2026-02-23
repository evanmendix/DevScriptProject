@echo off
REM 自動點擊腳本環境設定檔案

echo 🚀 設定自動點擊腳本環境...
echo.

REM 檢查 Python 是否已安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 找不到 Python，請先安裝 Python 3.12+
    echo 下載網址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python 已安裝
python --version

REM 安裝所需套件
echo.
echo 📦 安裝所需套件...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ 套件安裝失敗，請檢查網路連線或嘗試手動安裝：
    echo pip install pyautogui Pillow opencv-python
    pause
    exit /b 1
)

echo.
echo ✅ 環境設定完成！
echo.
echo 📝 使用說明：
echo 1. 將目標圖片放入 target_images\ 目錄
echo 2. 執行 python auto_click.py 開始自動點擊
echo 3. 按 Ctrl+C 停止腳本
echo.
echo 📖 詳細說明請參考 README.md
echo.
pause
