import os
import subprocess
import customtkinter as ctk
from typing import Dict, List
from pathlib import Path
import json
from tkinter import filedialog
from customtkinter import CTkInputDialog
import threading
import queue
import sys

class ScriptLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 設定視窗
        self.title("Windows Script Launcher")
        self.geometry("800x600")
        
        # 使用系統預設的深色/淺色模式
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # --- New UI Layout ---
        self.grid_columnconfigure(0, weight=2) # Script list (slimmer)
        self.grid_columnconfigure(1, weight=5) # Control/Output pane (wider)
        self.grid_rowconfigure(0, weight=1)

        # --- Left Pane ---
        self.left_pane = ctk.CTkFrame(self, fg_color="transparent")
        self.left_pane.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="nsew")
        self.left_pane.grid_rowconfigure(1, weight=1)
        self.left_pane.grid_columnconfigure(0, weight=1)

        # Filter and Search Frame
        self.filter_frame = ctk.CTkFrame(self.left_pane)
        self.filter_frame.grid(row=0, column=0, padx=0, pady=(0, 10), sticky="ew")
        self.filter_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="搜尋...")
        self.search_entry.grid(row=0, column=0, padx=(0,10), pady=5, sticky="ew")

        self.filter_var = ctk.StringVar(value="ALL")
        self.filter_button = ctk.CTkSegmentedButton(
            self.filter_frame,
            values=["ALL", "PY", "BAT", "PS1"],
            variable=self.filter_var,
            command=self._on_search_filter_change
        )
        self.filter_button.grid(row=0, column=1, padx=0, pady=5)

        self.search_entry.bind("<KeyRelease>", self._on_search_filter_change)

        # Script List Frame (inside the left pane)
        self.script_list_frame = ctk.CTkScrollableFrame(self.left_pane, label_text="腳本列表")
        self.script_list_frame.grid(row=1, column=0, sticky="nsew")
        self.script_list_frame.grid_columnconfigure(0, weight=1)

        # Right Pane: Control and Output
        self.control_pane = ctk.CTkFrame(self)
        self.control_pane.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.control_pane.grid_rowconfigure(1, weight=1)
        self.control_pane.grid_columnconfigure(0, weight=1)

        self.selected_script_label = ctk.CTkLabel(self.control_pane, text="請從左側選擇一個腳本", font=ctk.CTkFont(size=16, weight="bold"))
        self.selected_script_label.grid(row=0, column=0, padx=10, pady=(10,0), sticky="w")

        self.console_output = ctk.CTkTextbox(self.control_pane, state="disabled")
        self.console_output.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.button_frame = ctk.CTkFrame(self.control_pane)
        self.button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        # --- End New UI Layout ---

        # --- Config and State ---
        self.config_file = Path(__file__).parent / "scripts.json"
        self.scripts_config: List[Dict] = []
        self.selected_script: Dict | None = None
        self.add_script_window = None
        self.log_queue = queue.Queue()
        self.running_processes: Dict[str, subprocess.Popen] = {}

        self.load_or_create_config()
        self.populate_scripts_ui()
        self.process_log_queue() # Start queue listener
        # --- End Config and State ---

    def open_add_script_window(self):
        """開啟用於新增/編輯腳本的彈出視窗。"""
        if self.add_script_window is None or not self.add_script_window.winfo_exists():
            self.add_script_window = AddScriptWindow(master=self)
            self.add_script_window.grab_set()
        else:
            self.add_script_window.focus()

    def load_or_create_config(self):
        """載入 scripts.json 設定檔，若不存在則建立。"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.scripts_config = json.load(f)
            except (json.JSONDecodeError, TypeError):
                self.scripts_config = []
                self.save_config()
                self.show_error("設定檔 'scripts.json' 毀損或格式錯誤，已重設。")
        else:
            # 如果檔案不存在，用一個範例腳本建立它
            self.scripts_config = [
                {
                    "name": "範例: 檢查 WiFi (一次性)",
                    "path": str(Path("windows/network/check_wifi2.bat").absolute()),
                    "type": "one-time"
                }
            ]
            self.save_config()

    def save_config(self):
        """將目前的腳本設定存回 scripts.json。"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.scripts_config, f, indent=4, ensure_ascii=False)

    def populate_scripts_ui(self):
        """根據搜尋和篩選條件，在左側列表中填入腳本按鈕。"""
        # 1. Get filter values
        search_term = self.search_entry.get().lower()
        filter_type = self.filter_var.get()

        # 2. Filter the scripts
        filtered_scripts = []
        for script in self.scripts_config:
            # Check filter type
            type_match = False
            if filter_type == "ALL":
                type_match = True
            else:
                suffix = "." + filter_type.lower()
                if script.get("path", "").lower().endswith(suffix):
                    type_match = True

            # Check search term
            name_match = False
            if search_term in script.get("name", "").lower():
                name_match = True

            if type_match and name_match:
                filtered_scripts.append(script)

        # 3. Display the filtered list
        for widget in self.script_list_frame.winfo_children():
            widget.destroy()

        add_button = ctk.CTkButton(self.script_list_frame, text="＋ 新增腳本", command=self.open_add_script_window)
        add_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        for i, script_data in enumerate(filtered_scripts, start=1):
            name = script_data.get("name", "未命名腳本")
            button = ctk.CTkButton(
                self.script_list_frame,
                text=name,
                command=lambda s=script_data: self.select_script(s)
            )
            button.grid(row=i, column=0, padx=10, pady=5, sticky="ew")

            tooltip_text = f"路徑: {script_data.get('path', 'N/A')}\n類型: {script_data.get('type', 'N/A')}"
            self.create_tooltip(button, tooltip_text)

    def select_script(self, script_data: Dict):
        """當使用者從左側列表選擇一個腳本時呼叫，並更新右側UI。"""
        self.selected_script = script_data

        self.selected_script_label.configure(text=script_data.get("name", "未命名腳本"))

        self.update_console_output(f"已選擇腳本: {script_data.get('name')}\n"
                                     f"路徑: {script_data.get('path')}\n"
                                     f"類型: {script_data.get('type')}\n", clear=True)

        self.update_control_buttons()

    def update_control_buttons(self):
        """根據選擇的腳本及其狀態，更新控制按鈕。"""
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        if not self.selected_script:
            return

        script_path = self.selected_script.get('path')
        script_type = self.selected_script.get('type')

        if script_type == 'one-time':
            # Disable button if any script is running to prevent conflicts
            is_any_script_running = bool(self.running_processes)
            run_button = ctk.CTkButton(self, text="執行", command=self.start_script_execution, state="disabled" if is_any_script_running else "normal")
            run_button.pack(in_=self.button_frame, side="left", padx=5)
            if is_any_script_running:
                self.create_tooltip(run_button, "已有背景腳本在執行中，無法執行一次性腳本。")

        elif script_type == 'background':
            if script_path in self.running_processes:
                stop_button = ctk.CTkButton(self.button_frame, text="停止", command=self.stop_script_execution, fg_color="#D32F2F")
                stop_button.pack(side="left", padx=5)
            else:
                start_button = ctk.CTkButton(self.button_frame, text="啟動", command=self.start_script_execution, fg_color="#388E3C")
                start_button.pack(side="left", padx=5)

        # Add rename button if a script is selected
        rename_button = ctk.CTkButton(self.button_frame, text="重新命名", command=self._on_rename_button_click, fg_color="gray")
        rename_button.pack(side="right", padx=5)

    def start_script_execution(self):
        """在一個新的執行緒中啟動所選的腳本。"""
        if not self.selected_script:
            return

        path = self.selected_script.get('path')
        if not path:
            self.show_error("錯誤：腳本路徑無效。")
            return

        self.update_console_output(f"--- 開始執行 {self.selected_script.get('name')} ---\n", clear=True)

        thread = threading.Thread(target=self._execute_script_worker, args=(path,), daemon=True)
        thread.start()

        self.update_control_buttons()


    def stop_script_execution(self):
        """停止所選的背景腳本。"""
        if not self.selected_script:
            return

        path = self.selected_script.get('path')
        if path in self.running_processes:
            process = self.running_processes.pop(path)
            # Use taskkill to terminate the process and its children
            try:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.log_queue.put(f"\n--- 腳本 {self.selected_script.get('name')} 已手動停止 ---\n")
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                # Fallback to terminate if taskkill fails
                process.terminate()
                self.log_queue.put(f"\n--- 腳本 {self.selected_script.get('name')} 已終止 (taskkill失敗) ---\n")

        self.update_control_buttons()

    def _on_rename_button_click(self):
        if not self.selected_script:
            return

        dialog = CTkInputDialog(
            text="請輸入新的腳本名稱:",
            title="重新命名腳本"
        )
        new_name = dialog.get_input()

        if new_name and new_name.strip():
            new_name = new_name.strip()
            script_path = self.selected_script.get("path")

            for script in self.scripts_config:
                if script.get("path") == script_path:
                    script["name"] = new_name
                    break

            self.save_config()
            self.selected_script["name"] = new_name

            self.populate_scripts_ui()
            self.selected_script_label.configure(text=new_name)

    def _on_search_filter_change(self, event=None):
        """Called when search or filter changes. Refreshes the script list."""
        self.populate_scripts_ui()

    def _find_venv_root(self, script_path: Path) -> Path | None:
        """從腳本位置向上搜尋最多10層，尋找 venv 或 .venv 目錄。"""
        current_dir = script_path.parent
        for _ in range(10):
            if (current_dir / "venv").is_dir() or (current_dir / ".venv").is_dir():
                return current_dir

            # If we've reached the root, stop.
            if current_dir.parent == current_dir:
                return None

            current_dir = current_dir.parent

        return None

    def _execute_script_worker(self, script_path_str: str):
        """[Worker Thread] 執行腳本，並將輸出傳遞到佇列。"""
        try:
            script_path = Path(script_path_str)
            command = []
            cwd = None

            if script_path.suffix == ".py":
                venv_root = self._find_venv_root(script_path)
                if venv_root:
                    self.log_queue.put(f"找到虛擬環境: {venv_root}，使用 uv run 執行...\n")
                    command = ["uv", "run", "python", script_path_str]
                    cwd = venv_root
                else:
                    self.log_queue.put(f"警告: 找不到虛擬環境，將使用系統 Python ({sys.executable}) 執行...\n")
                    command = [sys.executable, script_path_str]
                    cwd = script_path.parent
            elif script_path.suffix == ".ps1":
                command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path_str]
                cwd = script_path.parent
            else: # .bat and others
                command = [script_path_str]
                cwd = script_path.parent

            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            current_script_type = self.selected_script.get('type') if self.selected_script else None
            if current_script_type == 'background':
                self.running_processes[script_path_str] = process
                self.after(0, self.update_control_buttons)

            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    self.log_queue.put(line)
                process.stdout.close()

            return_code = process.wait()
            self.log_queue.put(f"\n--- 腳本執行完成，返回碼: {return_code} ---\n")

        except Exception as e:
            self.log_queue.put(f"\n--- 執行時發生錯誤: {e} ---\n")
        finally:
            if script_path_str in self.running_processes:
                self.running_processes.pop(script_path_str, None)
                self.after(0, self.update_control_buttons)

    def update_console_output(self, message: str, clear: bool = False):
        """安全地更新控制台文字框。"""
        self.console_output.configure(state="normal")
        if clear:
            self.console_output.delete("1.0", "end")
        self.console_output.insert("end", message)
        self.console_output.see("end")
        self.console_output.configure(state="disabled")

    def process_log_queue(self):
        """從佇列中處理日誌訊息並更新UI。"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                if message is None: # Sentinel value to update buttons
                    self.update_control_buttons()
                else:
                    self.update_console_output(message)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_log_queue)

    def show_error(self, message: str):
        error_window = ctk.CTkToplevel(self)
        error_window.title("錯誤")
        error_window.geometry("400x200")
        
        label = ctk.CTkLabel(error_window, text=message)
        label.pack(padx=20, pady=20)
        
        button = ctk.CTkButton(error_window, text="確定", command=error_window.destroy)
        button.pack(pady=20)

    def create_tooltip(self, widget, text):
        tooltip = ctk.CTkToplevel(self)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        
        label = ctk.CTkLabel(tooltip, text=text)
        label.pack()
        
        def show_tooltip(event):
            tooltip.deiconify()
            tooltip.geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        def hide_tooltip(event):
            tooltip.withdraw()
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
        
        return tooltip

# ==============================================================================
# 新增/編輯腳本的彈出視窗
# ==============================================================================
class AddScriptWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master_app = master

        self.title("新增腳本")
        self.geometry("500x300")

        self.grid_columnconfigure(1, weight=1)

        # --- Widgets ---
        # 腳本路徑
        self.path_label = ctk.CTkLabel(self, text="腳本路徑:")
        self.path_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.path_entry = ctk.CTkEntry(self, state="disabled")
        self.path_entry.grid(row=0, column=1, padx=20, pady=10, sticky="ew")
        self.browse_button = ctk.CTkButton(self, text="瀏覽...", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=20, pady=10)

        # 腳本名稱
        self.name_label = ctk.CTkLabel(self, text="顯示名稱:")
        self.name_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.name_entry = ctk.CTkEntry(self, placeholder_text="例如：備份伺服器")
        self.name_entry.grid(row=1, column=1, columnspan=2, padx=20, pady=10, sticky="ew")

        # 腳本類型
        self.type_label = ctk.CTkLabel(self, text="腳本類型:")
        self.type_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.type_menu = ctk.CTkOptionMenu(self, values=["one-time", "background"])
        self.type_menu.grid(row=2, column=1, columnspan=2, padx=20, pady=10, sticky="w")

        # 控制按鈕
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=3, column=0, columnspan=3, pady=20)

        self.save_button = ctk.CTkButton(self.button_frame, text="儲存", command=self.save_script)
        self.save_button.pack(side="left", padx=10)
        self.cancel_button = ctk.CTkButton(self.button_frame, text="取消", command=self.destroy, fg_color="gray")
        self.cancel_button.pack(side="left", padx=10)

    def browse_file(self):
        filepath = filedialog.askopenfilename(
            title="選擇一個腳本檔案",
            filetypes=(
                ("Scripts", "*.py *.bat *.ps1"),
                ("Python Scripts", "*.py"),
                ("Batch Files", "*.bat"),
                ("PowerShell Scripts", "*.ps1"),
                ("All files", "*.*")
            )
        )
        if filepath:
            self.path_entry.configure(state="normal")
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, filepath)
            self.path_entry.configure(state="disabled")
            # 自動填入名稱
            if not self.name_entry.get():
                self.name_entry.insert(0, Path(filepath).stem)

    def save_script(self):
        path = self.path_entry.get()
        name = self.name_entry.get()
        script_type = self.type_menu.get()

        if not path or not name:
            self.master_app.show_error("錯誤：腳本路徑和顯示名稱不能為空。")
            return

        new_script = {
            "name": name,
            "path": path,
            "type": script_type
        }

        self.master_app.scripts_config.append(new_script)
        self.master_app.save_config()
        # Destroy the window *before* refreshing the main UI to avoid race conditions
        self.destroy()
        self.master_app.populate_scripts_ui()


if __name__ == "__main__":
    app = ScriptLauncher()
    app.mainloop()
