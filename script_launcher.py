import os
import subprocess
import customtkinter as ctk
from typing import Dict, List
from pathlib import Path

class ScriptLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 設定視窗
        self.title("Windows Script Launcher")
        self.geometry("800x600")
        
        # 使用系統預設的深色/淺色模式
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # 建立主要容器
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 建立分頁容器
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # 定義腳本目錄
        self.windows_dir = Path(__file__).parent / "windows"
        
        # 建立分頁和按鈕
        self.create_tabs()

    def create_tabs(self):
        # 取得所有子目錄
        subdirs = [d for d in self.windows_dir.iterdir() if d.is_dir()]
        
        # 為每個子目錄建立分頁
        for subdir in subdirs:
            tab_name = subdir.name.replace("_", " ").title()
            self.tabview.add(tab_name)
            tab = self.tabview.tab(tab_name)
            
            # 設定分頁的網格
            tab.grid_columnconfigure(0, weight=1)
            
            # 在分頁中加入腳本按鈕
            scripts = list(subdir.glob("*.bat"))
            for i, script in enumerate(scripts):
                button = ctk.CTkButton(
                    tab,
                    text=script.stem.replace("_", " ").title(),
                    command=lambda s=script: self.run_script(s)
                )
                button.grid(row=i, column=0, padx=20, pady=10, sticky="ew")
                
                # 加入提示文字
                tooltip = self.create_tooltip(button, self.get_script_description(script))

    def run_script(self, script_path: Path):
        try:
            # 使用系統管理員權限執行腳本
            subprocess.run(["powershell", "Start-Process", str(script_path), "-Verb", "RunAs"],
                         check=True)
        except subprocess.CalledProcessError as e:
            self.show_error(f"執行失敗: {e}")
        except Exception as e:
            self.show_error(f"發生錯誤: {e}")

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

    def get_script_description(self, script_path: Path) -> str:
        """從 README.md 中取得腳本的描述"""
        readme_path = script_path.parent.parent / "README.md"
        if not readme_path.exists():
            return "無描述"
            
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 尋找腳本名稱和描述
            script_name = script_path.name
            for line in content.split('\n'):
                if script_name in line and '-' in line:
                    return line.split('-', 1)[1].strip()
            
            return "無描述"
        except Exception:
            return "無描述"

if __name__ == "__main__":
    app = ScriptLauncher()
    app.mainloop()
