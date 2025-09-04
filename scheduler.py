import subprocess
from datetime import datetime, time, date
from pathlib import Path
import time as time_module

# Paths relative to this file
BASE = Path(__file__).resolve().parent
SCREEN_DIR = BASE / "windows" / "screen_control"

BAT_EXTEND = SCREEN_DIR / "screen_extend.bat"
BAT_INTERNAL = SCREEN_DIR / "screen_internal.bat"
PS1_BRIGHTNESS = SCREEN_DIR / "brightness.ps1"
PS1_POWER = SCREEN_DIR / "screen_power.ps1"

MORNING_AT = time(8, 30)   # 08:30
EVENING_AT = time(19, 00)   # 19:00

# Trigger window (seconds) to avoid multiple fires due to loop timing
TRIGGER_WINDOW_SEC = 120
SLEEP_INTERVAL_SEC = 20


def is_weekday(dt: datetime) -> bool:
    # Monday=0 .. Sunday=6
    return dt.weekday() < 5


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


def screen_power(state: str) -> None:
    if state not in ("On", "Off", "Dim"):
        raise ValueError("state must be 'On', 'Off', or 'Dim'")
    switch = f"-{state}"
    run_cmd([
        "powershell", "-ExecutionPolicy", "Bypass", "-File", str(PS1_POWER), switch
    ])


def morning_routine() -> None:
    # 1) Extend display  2) Turn-on screen  3) Brightness to max
    print(f"[{datetime.now()}] Morning routine started")
    set_display_mode("extend")
    screen_power("On")
    set_brightness(100)
    print(f"[{datetime.now()}] Morning routine finished")


def evening_routine() -> None:
    # 1) Internal-only  2) Brightness to min  3) Turn-off screen
    print(f"[{datetime.now()}] Evening routine started")
    set_display_mode("internal")
    # Soft off: only dim brightness to 0 to avoid hardware power-off issues
    set_brightness(0)
    # Use Dim (low-power) to emulate system screen-off behavior while staying easy to wake
    try:
        screen_power("Dim")
    except Exception as e:
        print(f"Dim attempt failed, keeping soft off only: {e}")
    print(f"[{datetime.now()}] Evening routine finished (dim)")


def within_window(now: datetime, target: time, window_sec: int) -> bool:
    target_dt = now.replace(hour=target.hour, minute=target.minute, second=0, microsecond=0)
    delta = abs((now - target_dt).total_seconds())
    return delta <= window_sec


def main() -> None:
    last_morning_run: date | None = None
    last_evening_run: date | None = None

    print("Scheduler started. Weekdays 08:30 and 19:00 routines will run.")

    while True:
        now = datetime.now()
        if is_weekday(now):
            # Morning
            if within_window(now, MORNING_AT, TRIGGER_WINDOW_SEC):
                if last_morning_run != now.date():
                    try:
                        morning_routine()
                        last_morning_run = now.date()
                    except Exception as e:
                        print(f"Morning routine error: {e}")
            # Evening
            if within_window(now, EVENING_AT, TRIGGER_WINDOW_SEC):
                if last_evening_run != now.date():
                    try:
                        evening_routine()
                        last_evening_run = now.date()
                    except Exception as e:
                        print(f"Evening routine error: {e}")
        # Sleep
        time_module.sleep(SLEEP_INTERVAL_SEC)


if __name__ == "__main__":
    main()
