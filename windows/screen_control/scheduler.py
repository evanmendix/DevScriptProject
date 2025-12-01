from datetime import datetime, time, date
import time as time_module

from windows.screen_control.screen_utils import screen_power_up, screen_power_down

MORNING_AT = time(8, 30)
EVENING_AT = time(18, 15)

# Trigger window (seconds) to avoid multiple fires due to loop timing
TRIGGER_WINDOW_SEC = 120
SLEEP_INTERVAL_SEC = 20


def is_weekday(dt: datetime) -> bool:
    # Monday=0 .. Sunday=6
    return dt.weekday() < 5


# def screen_power(state: str) -> None:
#     if state not in ("On", "Off", "Dim"):
#         raise ValueError("state must be 'On', 'Off', or 'Dim'")
#     switch = f"-{state}"
#     run_cmd([
#         "powershell", "-ExecutionPolicy", "Bypass", "-File", str(PS1_POWER), switch
#     ])


def within_window(now: datetime, target: time, window_sec: int) -> bool:
    target_dt = now.replace(hour=target.hour, minute=target.minute, second=0, microsecond=0)
    delta = abs((now - target_dt).total_seconds())
    return delta <= window_sec


def main() -> None:
    last_morning_run: date | None = None
    last_evening_run: date | None = None

    print("Scheduler started. Weekdays 08:30 and 18:15 routines will run.")

    while True:
        now = datetime.now()
        if is_weekday(now):
            # Morning
            if within_window(now, MORNING_AT, TRIGGER_WINDOW_SEC):
                if last_morning_run != now.date():
                    try:
                        screen_power_up()
                        last_morning_run = now.date()
                    except Exception as e:
                        print(f"Morning routine error: {e}")
            # Evening
            if within_window(now, EVENING_AT, TRIGGER_WINDOW_SEC):
                if last_evening_run != now.date():
                    try:
                        screen_power_down()
                        last_evening_run = now.date()
                    except Exception as e:
                        print(f"Evening routine error: {e}")
        # Sleep
        time_module.sleep(SLEEP_INTERVAL_SEC)


if __name__ == "__main__":
    main()
