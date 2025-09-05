# 系統設計 (System Design)

本文件詳細描述了應用程式的內部軟體設計、元件以及它們之間的互動。

---

### 1. 主要類別與元件

- **`ScriptLauncher(customtkinter.CTk)`**:
    - **職責**: 作為主應用程式的進入點和核心協調者。它管理著主視窗的佈局、所有 UI 元件的狀態，並處理使用者互動事件。
    - **核心屬性**:
        - `scripts_config: List[Dict]`: 從 `scripts.json` 載入的腳本設定主列表。
        - `selected_script: Dict | None`: 當前在 UI 上被選中的腳本物件。
        - `running_processes: Dict[str, subprocess.Popen]`: 一個字典，用於追蹤正在執行的背景程序。鍵是腳本路徑，值是 `subprocess.Popen` 物件。
        - `log_queue: queue.Queue`: 一個執行緒安全的佇列，用於從背景工作執行緒向主 UI 執行緒傳遞日誌訊息。

- **`AddScriptWindow(customtkinter.CTkToplevel)`**:
    - **職責**: 一個模態對話框，用於「新增」和「編輯」腳本。
    - **模式**: 透過傳入的 `script_to_edit` 物件來決定自身處於「新增」或「編輯」模式。
    - **核心邏輯**:
        - 在編輯模式下，會預先填入表單資料。
        - 儲存時，會根據模式來決定是新增一筆資料到主設定檔中，還是更新既有的資料。

- **`scripts.json`**:
    - **職責**: 作為應用的資料持久化層。它是一個簡單的 JSON 檔案，儲存一個包含腳本物件的陣列。
    - **結構**:
        ```json
        [
          {
            "name": "顯示名稱",
            "path": "C:/path/to/script.bat",
            "type": "one-time"
          }
        ]
        ```

### 2. 核心邏輯設計

#### 2.1 非同步腳本執行
為了防止在執行腳本時 UI 凍結，應用程式採用了多執行緒模型。
1.  **啟動**: 當使用者點擊「執行」或「啟動」時，`start_script_execution` 方法會建立一個新的 `threading.Thread`，並將 `_execute_script_worker` 方法作為其目標。
2.  **工作執行緒 (`_execute_script_worker`)**:
    - 此方法在背景執行緒中運行。
    - 它使用 `subprocess.Popen` 來啟動子程序，並將 `stdout` 和 `stderr` 重導向到 `PIPE`。
    - 它以非同步方式逐行讀取子程序的輸出，並將每一行放入 `log_queue` 中。
    - 這種設計確保了即使腳本有大量輸出或長時間運行，UI 也能即時回應。
3.  **UI 更新 (`process_log_queue`)**:
    - 主 UI 執行緒透過 `self.after()` 方法，每 100 毫秒輪詢一次 `log_queue`。
    - 如果佇列中有新的日誌訊息，它會安全地將其取出並更新到主控台文字框中。這是從背景執行緒安全更新 Tkinter UI 的標準模式。

#### 2.2 Python 虛擬環境偵測
`_execute_script_worker` 中包含針對 Python 腳本的特殊處理邏輯。
1.  **搜尋**: 當執行 `.py` 檔案時，會先呼叫輔助函式 `_find_venv_root`。
2.  **`_find_venv_root`**: 此函式實作了從腳本所在目錄向上尋找 `venv` 或 `.venv` 資料夾的邏輯，最多 10 層。
3.  **執行**:
    - **找到 venv**: `subprocess.Popen` 會被設定 `cwd` (當前工作目錄) 參數為 venv 所在的專案根目錄，並使用 `uv run python ...` 指令來執行。
    - **未找到 venv**: 會使用 `sys.executable` (當前啟動器自身的 Python 解譯器) 來執行腳本，並在主控台輸出警告。

#### 2.3 狀態管理與 UI 刷新
- 應用程式的狀態主要由 `self.scripts_config` 和 `self.selected_script` 驅動。
- 任何可能改變腳本列表顯示的動作（例如搜尋、篩選、新增、編輯、移除）最終都會呼叫 `populate_scripts_ui` 方法。
- `populate_scripts_ui` 會根據當前的搜尋和篩選條件，從 `self.scripts_config` 過濾出一個臨時列表，並用它來重新繪製整個腳本列表 UI。這種「單向資料流」的設計使得 UI 狀態的管理變得簡單和可預測。
