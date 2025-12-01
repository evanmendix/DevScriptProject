import os
import subprocess
import customtkinter as ctk
from typing import Dict, List, Tuple, Union, Set
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
            values=["ALL", "PY", "BAT", "PS1", "STARTUP"],
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

        # Header Frame for label and close button
        self.header_frame = ctk.CTkFrame(self.control_pane, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=10, pady=(10,0), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.selected_script_label = ctk.CTkLabel(self.header_frame, text="請從左側選擇一個腳本", font=ctk.CTkFont(size=16, weight="bold"))
        self.selected_script_label.grid(row=0, column=0, sticky="w")

        self.close_tab_button = ctk.CTkButton(self.header_frame, text="關閉分頁", width=80, fg_color="gray", command=self.close_current_tab)
        self.close_tab_button.grid(row=0, column=1, sticky="e")

        # Replaced single console_output with tab view
        self.console_tabs = ctk.CTkTabview(self.control_pane)
        self.console_tabs.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Store log widgets and tab names
        self.log_widgets: Dict[str, ctk.CTkTextbox] = {}
        self.log_id_to_tab_name: Dict[str, str] = {}

        # Initialize Main Console
        self._ensure_log_tab("MAIN", "主控制台")

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
        self.starting_scripts: Set[str] = set()

        self.load_or_create_config()
        self.populate_scripts_ui()
        self.process_log_queue() # Start queue listener
        # --- End Config and State ---

    def _ensure_log_tab(self, log_id: str, tab_name: str) -> ctk.CTkTextbox:
        """Ensures a tab exists for the given log_id and returns the textbox widget."""
        if log_id in self.log_widgets:
            return self.log_widgets[log_id]

        # Handle potential tab name conflicts
        final_tab_name = tab_name
        counter = 1
        while True:
            # Check if tab name is already used by another log_id
            name_used = False
            for existing_id, name in self.log_id_to_tab_name.items():
                if name == final_tab_name:
                    name_used = True
                    break

            if not name_used:
                try:
                    tab = self.console_tabs.add(final_tab_name)
                    break
                except ValueError:
                    # Should be covered by name_used check, but just in case
                    pass

            final_tab_name = f"{tab_name} ({counter})"
            counter += 1

        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        textbox = ctk.CTkTextbox(tab, state="disabled")
        textbox.grid(row=0, column=0, sticky="nsew")

        self.log_widgets[log_id] = textbox
        self.log_id_to_tab_name[log_id] = final_tab_name
        return textbox

    def close_current_tab(self):
        """Closes the currently selected tab if it's not the main console and script is not running."""
        current_tab_name = self.console_tabs.get()

        # Find log_id for this tab name
        target_log_id = None
        for log_id, name in self.log_id_to_tab_name.items():
            if name == current_tab_name:
                target_log_id = log_id
                break

        if not target_log_id:
            return # Should not happen

        if target_log_id == "MAIN":
            self.show_error("無法關閉主控制台。")
            return

        if target_log_id in self.running_processes or target_log_id in self.starting_scripts:
            self.show_error("無法關閉正在執行或啟動中腳本的分頁。")
            return

        # Safe to close
        self.console_tabs.delete(current_tab_name)
        del self.log_widgets[target_log_id]
        del self.log_id_to_tab_name[target_log_id]

    def open_add_script_window(self, script_to_edit: Dict | None = None):
        """開啟用於新增/編輯腳本的彈出視窗。"""
        if self.add_script_window is None or not self.add_script_window.winfo_exists():
            self.add_script_window = AddScriptWindow(master=self, script_to_edit=script_to_edit)
            self.add_script_window.grab_set()
        else:
            self.add_script_window.focus()

    def _on_edit_button_click(self):
        """Called when the 'Edit' button is clicked."""
        if self.selected_script:
            self.open_add_script_window(script_to_edit=self.selected_script)

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
            # If the file doesn't exist, create an empty one.
            self.scripts_config = []
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
            elif filter_type == "STARTUP":
                if script.get("type") == "startup":
                    type_match = True
            else:
                suffix = "." + filter_type.lower()
                if script.get("path", "").lower().endswith(suffix) or script.get("setup_path", "").lower().endswith(suffix):
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

        # Log selection to MAIN console
        self.update_console_output(f"已選擇腳本: {script_data.get('name')}\n"
                                     f"路徑: {script_data.get('path')}\n"
                                     f"類型: {script_data.get('type')}\n", log_id="MAIN", clear=True)

        # If it's a running background script, maybe switch to its tab?
        path = script_data.get('path')
        if script_data.get('type') == 'background' and path in self.running_processes:
            if path in self.log_id_to_tab_name:
                self.console_tabs.set(self.log_id_to_tab_name[path])

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
            # Enabled even if other scripts are running
            # Also disabled if THIS specific one-time script is somehow running? (Unlikely for one-time unless blocked)
            # Actually one-time scripts run and finish.
            # But let's check starting_scripts just in case logic changes.
            run_button = ctk.CTkButton(self.button_frame, text="執行", command=self.start_script_execution)
            run_button.pack(side="left", padx=5)

        elif script_type == 'background':
            is_starting = script_path in self.starting_scripts
            if script_path in self.running_processes:
                stop_button = ctk.CTkButton(self.button_frame, text="停止", command=self.stop_script_execution, fg_color="#D32F2F")
                stop_button.pack(side="left", padx=5)
            elif is_starting:
                start_button = ctk.CTkButton(self.button_frame, text="啟動中...", state="disabled", fg_color="#388E3C")
                start_button.pack(side="left", padx=5)
            else:
                start_button = ctk.CTkButton(self.button_frame, text="啟動", command=self.start_script_execution, fg_color="#388E3C")
                start_button.pack(side="left", padx=5)
                
        elif script_type == 'startup':
            startup_file = self.selected_script.get('startup_file', '')
            if startup_file and self._check_startup_status(startup_file):
                disable_button = ctk.CTkButton(self.button_frame, text="停用自動啟動", command=self.disable_startup, fg_color="#D32F2F")
                disable_button.pack(side="left", padx=5)
                status_label = ctk.CTkLabel(self.button_frame, text="✓ 已啟用", text_color="#388E3C")
                status_label.pack(side="left", padx=10)
            else:
                enable_button = ctk.CTkButton(self.button_frame, text="啟用自動啟動", command=self.enable_startup, fg_color="#388E3C")
                enable_button.pack(side="left", padx=5)
                status_label = ctk.CTkLabel(self.button_frame, text="✗ 未啟用", text_color="#D32F2F")
                status_label.pack(side="left", padx=10)

        # Add management buttons on the left
        edit_button = ctk.CTkButton(self.button_frame, text="編輯", command=self._on_edit_button_click, fg_color="gray")
        edit_button.pack(side="left", padx=10)
        rename_button = ctk.CTkButton(self.button_frame, text="重新命名", command=self._on_rename_button_click, fg_color="gray")
        rename_button.pack(side="left", padx=5)

        # Add destructive button on the far right
        delete_button = ctk.CTkButton(self.button_frame, text="移除", command=self._on_delete_button_click, fg_color="#D32F2F")
        delete_button.pack(side="right", padx=5)

    def start_script_execution(self):
        """在一個新的執行緒中啟動所選的腳本。"""
        if not self.selected_script:
            return

        path = self.selected_script.get('path')
        name = self.selected_script.get('name')
        if not path:
            self.show_error("錯誤：腳本路徑無效。")
            return

        log_id = "MAIN"
        script_type = self.selected_script.get('type')
        if script_type == 'background':
            log_id = path
            # Check if already running or starting
            if path in self.running_processes or path in self.starting_scripts:
                self.show_error("此腳本已在執行或啟動中。")
                return

            # Mark as starting
            self.starting_scripts.add(path)

            self._ensure_log_tab(log_id, name)
            # Switch to the tab
            if log_id in self.log_id_to_tab_name:
                self.console_tabs.set(self.log_id_to_tab_name[log_id])
        else:
            self.console_tabs.set("主控制台")

        self.update_console_output(f"--- 開始執行 {name} ---\n", log_id=log_id, clear=True)

        thread = threading.Thread(target=self._execute_script_worker, args=(path, log_id), daemon=True)
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
                self.log_queue.put((path, f"\n--- 腳本 {self.selected_script.get('name')} 已手動停止 ---\n"))
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                # Fallback to terminate if taskkill fails
                process.terminate()
                self.log_queue.put((path, f"\n--- 腳本 {self.selected_script.get('name')} 已終止 (taskkill失敗) ---\n"))

        self.update_control_buttons()

    def enable_startup(self):
        """啟用所選的自動啟動腳本。"""
        if not self.selected_script or self.selected_script.get('type') != 'startup':
            return

        setup_path = self.selected_script.get('setup_path')
        if not setup_path:
            self.show_error("錯誤：找不到設置腳本路徑。")
            return

        self.update_console_output(f"--- 啟用自動啟動: {self.selected_script.get('name')} ---\n", log_id="MAIN", clear=True)

        thread = threading.Thread(target=self._execute_script_worker, args=(setup_path, "MAIN"), daemon=True)
        thread.start()

    def disable_startup(self):
        """停用所選的自動啟動腳本。"""
        if not self.selected_script or self.selected_script.get('type') != 'startup':
            return

        remove_path = self.selected_script.get('remove_path')
        if not remove_path:
            self.show_error("錯誤：找不到移除腳本路徑。")
            return

        self.update_console_output(f"--- 停用自動啟動: {self.selected_script.get('name')} ---\n", log_id="MAIN", clear=True)

        thread = threading.Thread(target=self._execute_script_worker, args=(remove_path, "MAIN"), daemon=True)
        thread.start()

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

    def _on_delete_button_click(self):
        if not self.selected_script:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("確認移除")
        dialog.geometry("350x150")
        dialog.transient(self)
        dialog.grab_set()

        result = {"confirmed": False}

        def confirm():
            result["confirmed"] = True
            dialog.destroy()

        def cancel():
            dialog.destroy()

        label = ctk.CTkLabel(dialog, text=f"您確定要移除腳本 '{self.selected_script.get('name')}' 嗎？\n此操作無法復原。", wraplength=300)
        label.pack(padx=20, pady=20)

        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=10)

        no_button = ctk.CTkButton(button_frame, text="取消", command=cancel)
        no_button.pack(side="left", padx=10)
        yes_button = ctk.CTkButton(button_frame, text="確定移除", command=confirm, fg_color="#D32F2F")
        yes_button.pack(side="left", padx=10)

        self.wait_window(dialog)

        if result["confirmed"]:
            path_to_remove = self.selected_script.get("path")
            self.scripts_config = [s for s in self.scripts_config if s.get("path") != path_to_remove]
            self.save_config()

            self.selected_script = None
            self.populate_scripts_ui()
            self.update_control_buttons()
            self.selected_script_label.configure(text="請從左側選擇一個腳本")
            self.update_console_output("", log_id="MAIN", clear=True)

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

    def _check_startup_status(self, startup_file: str) -> bool:
        """檢查指定的啟動檔案是否存在於 Windows 啟動資料夾中。"""
        startup_folder = Path(os.environ.get('APPDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
        startup_path = startup_folder / startup_file
        return startup_path.exists()

    def _execute_script_worker(self, script_path_str: str, log_id: str):
        """[Worker Thread] 執行腳本，並將輸出傳遞到佇列。"""
        try:
            script_path = Path(script_path_str)
            command = []
            cwd = None

            if script_path.suffix == ".py":
                venv_root = self._find_venv_root(script_path)
                if venv_root:
                    self.log_queue.put((log_id, f"找到虛擬環境: {venv_root}，使用 uv run 執行...\n"))
                    command = ["uv", "run", "python", script_path_str]
                    cwd = venv_root
                else:
                    self.log_queue.put((log_id, f"警告: 找不到虛擬環境，將使用系統 Python ({sys.executable}) 執行...\n"))
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

            is_background = (log_id != "MAIN")

            if is_background:
                self.running_processes[script_path_str] = process
                # We can now safely remove from starting_scripts because process is in running_processes
                # However, this runs in a thread.
                # To be thread-safe for the UI logic that reads these sets, we should use `after` or simple atomic operations (GIL helps).
                # But better to just remove it here.
                # Note: `update_control_buttons` is called via `after` later.
                pass

            self.after(0, self.update_control_buttons)

            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    self.log_queue.put((log_id, line))
                process.stdout.close()

            return_code = process.wait()
            self.log_queue.put((log_id, f"\n--- 腳本執行完成，返回碼: {return_code} ---\n"))
            
            # For startup scripts, update buttons after execution to reflect new status
            if self.selected_script and self.selected_script.get('type') == 'startup':
                self.after(0, self.update_control_buttons)
            # Update buttons general (e.g. background script finished)
            self.after(0, self.update_control_buttons)

        except Exception as e:
            self.log_queue.put((log_id, f"\n--- 執行時發生錯誤: {e} ---\n"))
        finally:
            # Clean up starting state
            if script_path_str in self.starting_scripts:
                 # We must be careful. Python sets are thread-safe for add/remove?
                 # Yes, for single operations.
                 # But we should probably do it in main thread to avoid race with button update logic?
                 # Actually, update_control_buttons runs in main thread.
                 # If we remove it here, and running_processes update happened earlier, it's fine.
                 # Wait, where did we remove it from starting_scripts?
                 # I added `pass` above. I should remove it.
                 # Actually, I should remove it from starting_scripts AS SOON AS it is added to running_processes.
                 pass

            # If background script, remove from running processes
            if script_path_str in self.running_processes:
                self.running_processes.pop(script_path_str, None)

            # Also ensure it is removed from starting_scripts if it failed before starting
            if script_path_str in self.starting_scripts:
                 self.starting_scripts.remove(script_path_str)

            self.after(0, self.update_control_buttons)

    def update_console_output(self, message: str, log_id: str = "MAIN", clear: bool = False):
        """安全地更新控制台文字框。"""
        widget = self.log_widgets.get(log_id)
        if not widget:
            widget = self.log_widgets.get("MAIN")

        if widget:
            widget.configure(state="normal")
            if clear:
                widget.delete("1.0", "end")
            widget.insert("end", message)
            widget.see("end")
            widget.configure(state="disabled")

    def process_log_queue(self):
        """從佇列中處理日誌訊息並更新UI。"""
        try:
            while True:
                data = self.log_queue.get_nowait()
                if data is None: # Sentinel value to update buttons
                    self.update_control_buttons()
                elif isinstance(data, tuple):
                    log_id, message = data
                    self.update_console_output(message, log_id=log_id)
                else:
                    self.update_console_output(data, log_id="MAIN")
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

class AddScriptWindow(ctk.CTkToplevel):
    def __init__(self, master, script_to_edit: Dict | None = None):
        super().__init__(master)
        self.master_app = master
        self.script_to_edit = script_to_edit
        self.mode = "edit" if self.script_to_edit else "add"

        # --- Type Mapping ---
        self.type_display_map = {"one-time": "一次性", "background": "背景常駐", "startup": "自動啟動設置"}
        self.type_internal_map = {v: k for k, v in self.type_display_map.items()}

        if self.mode == "edit":
            self.title("編輯腳本")
        else:
            self.title("新增腳本")
        self.geometry("600x450")

        self.grid_columnconfigure(1, weight=1)

        # --- Widgets ---
        # 腳本路徑 (for one-time and background)
        self.path_label = ctk.CTkLabel(self, text="腳本路徑:")
        self.path_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.path_entry = ctk.CTkEntry(self, state="disabled")
        self.path_entry.grid(row=0, column=1, padx=20, pady=10, sticky="ew")
        self.browse_button = ctk.CTkButton(self, text="瀏覽...", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=20, pady=10)
        
        # Startup specific fields (initially hidden)
        self.setup_path_label = ctk.CTkLabel(self, text="設置腳本路徑:")
        self.setup_path_entry = ctk.CTkEntry(self, state="disabled")
        self.browse_setup_button = ctk.CTkButton(self, text="瀏覽...", command=self.browse_setup_file)
        
        self.remove_path_label = ctk.CTkLabel(self, text="移除腳本路徑:")
        self.remove_path_entry = ctk.CTkEntry(self, state="disabled")
        self.browse_remove_button = ctk.CTkButton(self, text="瀏覽...", command=self.browse_remove_file)
        
        self.startup_file_label = ctk.CTkLabel(self, text="啟動檔案名稱:")
        self.startup_file_entry = ctk.CTkEntry(self, placeholder_text="例如：Check_WiFi3_ORBI.vbs")

        # 腳本名稱
        self.name_label = ctk.CTkLabel(self, text="顯示名稱:")
        self.name_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.name_entry = ctk.CTkEntry(self, placeholder_text="例如：備份伺服器")
        self.name_entry.grid(row=1, column=1, columnspan=2, padx=20, pady=10, sticky="ew")

        # 腳本類型
        self.type_label = ctk.CTkLabel(self, text="腳本類型:")
        self.type_label.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        self.type_menu = ctk.CTkOptionMenu(self, values=list(self.type_display_map.values()), command=self.on_type_change)
        self.type_menu.grid(row=4, column=1, columnspan=2, padx=20, pady=10, sticky="w")

        # 控制按鈕
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=5, column=0, columnspan=3, pady=20)

        self.save_button = ctk.CTkButton(self.button_frame, text="儲存", command=self.save_script)
        self.save_button.pack(side="left", padx=10)
        self.cancel_button = ctk.CTkButton(self.button_frame, text="取消", command=self.destroy, fg_color="gray")
        self.cancel_button.pack(side="left", padx=10)

        # Initialize UI state
        self.on_type_change(self.type_menu.get())
        
        # Pre-fill fields if in edit mode
        if self.mode == "edit" and self.script_to_edit:
            stored_type = self.script_to_edit.get("type", "one-time")
            display_type = self.type_display_map.get(stored_type, "一次性")
            self.type_menu.set(display_type)
            self.on_type_change(display_type)
            
            self.name_entry.insert(0, self.script_to_edit.get("name", ""))
            
            if stored_type == "startup":
                # Fill startup-specific fields
                self.setup_path_entry.configure(state="normal")
                self.setup_path_entry.insert(0, self.script_to_edit.get("setup_path", ""))
                self.setup_path_entry.configure(state="disabled")
                
                self.remove_path_entry.configure(state="normal")
                self.remove_path_entry.insert(0, self.script_to_edit.get("remove_path", ""))
                self.remove_path_entry.configure(state="disabled")
                
                self.startup_file_entry.insert(0, self.script_to_edit.get("startup_file", ""))
                
                self.browse_setup_button.configure(state="disabled")
                self.browse_remove_button.configure(state="disabled")
            else:
                # Fill regular path field
                self.path_entry.configure(state="normal")
                self.path_entry.insert(0, self.script_to_edit.get("path", ""))
                self.path_entry.configure(state="disabled")
                self.browse_button.configure(state="disabled")

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

    def on_type_change(self, selected_type):
        """當腳本類型改變時，顯示或隱藏對應的欄位。"""
        script_type = self.type_internal_map.get(selected_type, "one-time")
        
        if script_type == "startup":
            # Hide regular path fields
            self.path_label.grid_remove()
            self.path_entry.grid_remove()
            self.browse_button.grid_remove()
            
            # Show startup-specific fields
            self.setup_path_label.grid(row=0, column=0, padx=20, pady=5, sticky="w")
            self.setup_path_entry.grid(row=0, column=1, padx=20, pady=5, sticky="ew")
            self.browse_setup_button.grid(row=0, column=2, padx=20, pady=5)
            
            self.remove_path_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
            self.remove_path_entry.grid(row=2, column=1, padx=20, pady=5, sticky="ew")
            self.browse_remove_button.grid(row=2, column=2, padx=20, pady=5)
            
            self.startup_file_label.grid(row=3, column=0, padx=20, pady=5, sticky="w")
            self.startup_file_entry.grid(row=3, column=1, columnspan=2, padx=20, pady=5, sticky="ew")
        else:
            # Show regular path fields
            self.path_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
            self.path_entry.grid(row=0, column=1, padx=20, pady=10, sticky="ew")
            self.browse_button.grid(row=0, column=2, padx=20, pady=10)
            
            # Hide startup-specific fields
            self.setup_path_label.grid_remove()
            self.setup_path_entry.grid_remove()
            self.browse_setup_button.grid_remove()
            self.remove_path_label.grid_remove()
            self.remove_path_entry.grid_remove()
            self.browse_remove_button.grid_remove()
            self.startup_file_label.grid_remove()
            self.startup_file_entry.grid_remove()

    def browse_setup_file(self):
        filepath = filedialog.askopenfilename(
            title="選擇設置腳本檔案",
            filetypes=(
                ("Scripts", "*.py *.bat *.ps1"),
                ("Batch Files", "*.bat"),
                ("PowerShell Scripts", "*.ps1"),
                ("All files", "*.*")
            )
        )
        if filepath:
            self.setup_path_entry.configure(state="normal")
            self.setup_path_entry.delete(0, "end")
            self.setup_path_entry.insert(0, filepath)
            self.setup_path_entry.configure(state="disabled")

    def browse_remove_file(self):
        filepath = filedialog.askopenfilename(
            title="選擇移除腳本檔案",
            filetypes=(
                ("Scripts", "*.py *.bat *.ps1"),
                ("Batch Files", "*.bat"),
                ("PowerShell Scripts", "*.ps1"),
                ("All files", "*.*")
            )
        )
        if filepath:
            self.remove_path_entry.configure(state="normal")
            self.remove_path_entry.delete(0, "end")
            self.remove_path_entry.insert(0, filepath)
            self.remove_path_entry.configure(state="disabled")

    def save_script(self):
        name = self.name_entry.get()
        display_type = self.type_menu.get()
        script_type = self.type_internal_map.get(display_type)

        if not name:
            self.master_app.show_error("錯誤：顯示名稱不能為空。")
            return

        if script_type == "startup":
            # Validate startup-specific fields
            setup_path = self.setup_path_entry.get()
            remove_path = self.remove_path_entry.get()
            startup_file = self.startup_file_entry.get()
            
            if not setup_path or not remove_path or not startup_file:
                self.master_app.show_error("錯誤：自動啟動設置類型需要填入所有欄位。")
                return
            
            script_data = {
                "name": name,
                "setup_path": setup_path,
                "remove_path": remove_path,
                "startup_file": startup_file,
                "type": script_type
            }
        else:
            # Regular script validation
            path = self.path_entry.get()
            if not path:
                self.master_app.show_error("錯誤：腳本路徑不能為空。")
                return
            
            script_data = {
                "name": name,
                "path": path,
                "type": script_type
            }

        if self.mode == "add":
            self.master_app.scripts_config.append(script_data)
        else:  # Edit mode
            # Find and update the existing script
            original_identifier = None
            if self.script_to_edit.get("type") == "startup":
                original_identifier = self.script_to_edit.get("setup_path")
            else:
                original_identifier = self.script_to_edit.get("path")
            
            for script in self.master_app.scripts_config:
                script_identifier = script.get("setup_path") if script.get("type") == "startup" else script.get("path")
                if script_identifier == original_identifier:
                    script.update(script_data)
                    break

        self.master_app.save_config()
        # Destroy the window *before* refreshing the main UI to avoid race conditions
        self.destroy()
        self.master_app.populate_scripts_ui()


if __name__ == "__main__":
    app = ScriptLauncher()
    app.mainloop()
