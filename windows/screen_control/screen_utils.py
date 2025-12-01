from datetime import datetime
import subprocess
from datetime import datetime, time, date
from pathlib import Path
import time as time_module

# Paths relative to this file
BASE = Path(__file__).resolve().parent.parent.parent
SCREEN_DIR = BASE / "windows" / "screen_control"

BAT_EXTEND = SCREEN_DIR / "screen_extend.bat"
BAT_INTERNAL = SCREEN_DIR / "screen_internal.bat"
PS1_BRIGHTNESS = SCREEN_DIR / "brightness.ps1"
PS1_POWER = SCREEN_DIR / "screen_power.ps1"

def run_cmd(args: list[str]) -> None:
    subprocess.run(args, check=True)


def run_cmd_cmdexe(script_path: Path) -> None:
    # For .bat files on Windows
    run_cmd(["cmd", "/c", str(script_path)])


def set_display_mode(mode: str) -> None:
    if mode == "extend":
        run_cmd_cmdexe(BAT_EXTEND)
    elif mode == "internal":
        run_cmd_cmdexe(BAT_INTERNAL)
    else:
        raise ValueError("Unsupported display mode")


def set_brightness(percent: int) -> None:
    percent = max(0, min(100, int(percent)))
    run_cmd([
        "powershell", "-ExecutionPolicy", "Bypass", "-File", str(PS1_BRIGHTNESS), "-Set", str(percent)
    ])

def screen_power_down() -> None:
    # 1) Internal-only  2) Brightness to min  3) Turn-off screen
    print(f"[{datetime.now()}] Evening routine started")
    set_display_mode("internal")
    # Soft off: only dim brightness to 0 to avoid hardware power-off issues
    set_brightness(0)
    # Use Dim (low-power) to emulate system screen-off behavior while staying easy to wake
    # try:
    #     screen_power("Dim")
    # except Exception as e:
    #     print(f"Dim attempt failed, keeping soft off only: {e}")
    print(f"[{datetime.now()}] Evening routine finished (dim)")


def screen_power_up() -> None:
    # 1) Extend display  2) Turn-on screen  3) Brightness to max
    print(f"[{datetime.now()}] Morning routine started")
    set_display_mode("extend")
    # screen_power("On")
    set_brightness(100)
    print(f"[{datetime.now()}] Morning routine finished")


if __name__ == "__main__":
    screen_power_up()
    screen_power_down()
