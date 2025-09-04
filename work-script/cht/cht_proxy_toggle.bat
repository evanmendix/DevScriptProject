@echo off
chcp 65001
setlocal enabledelayedexpansion

REM 檢查是否已經設置 http.proxy
git config --global --get http.proxy >nul 2>&1
if %errorlevel% equ 0 (
    REM 如果已經設置了 proxy，清除所有 proxy 設置
    git config --global --unset http.proxy
    git config --global --unset https.proxy
    echo Git proxy 已經清除。
   
    REM 清除 npm 和 yarn 的代理設置
    npm config delete proxy
    npm config delete https-proxy
    yarn config delete proxy
    yarn config delete https-proxy
    python -m pip config unset global.proxy
    echo npm, yarn, pip 的 proxy 已經清除。
) else (
    REM 如果未設置 proxy，設置 proxy
    git config --global http.proxy http://10.160.3.88:8080
    git config --global https.proxy http://10.160.3.88:8080
    echo Git proxy 已經設置為 http://10.160.3.88:8080。
   
    REM 設置 npm 和 yarn 的代理設置
    npm config set proxy http://10.160.3.88:8080
    npm config set https-proxy http://10.160.3.88:8080
    yarn config set proxy http://10.160.3.88:8080
    yarn config set https-proxy http://10.160.3.88:8080
    python -m pip config set global.proxy http://10.160.3.88:8080
    echo npm, yarn, pip 的 proxy 已經設置為 http://10.160.3.88:8080。
)

endlocal

REM 暫停以保持窗口打開
pause