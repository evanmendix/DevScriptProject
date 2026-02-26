#!/usr/bin/env python3
import screeninfo
import ctypes
from ctypes import wintypes

print("=== DPI 縮放檢測 ===")

# 檢查 screeninfo 結果
monitors = screeninfo.get_monitors()
for i, monitor in enumerate(monitors):
    print(f"\n螢幕 {i} (screeninfo):")
    print(f"  名稱: {monitor.name}")
    print(f"  位置: ({monitor.x}, {monitor.y})")
    print(f"  尺寸: {monitor.width} x {monitor.height}")
    print(f"  是否主螢幕: {monitor.is_primary}")

# 檢查 Windows DPI 設定
print("\n=== Windows DPI 檢測 ===")

class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('rcMonitor', wintypes.RECT),
        ('rcWork', wintypes.RECT),
        ('dwFlags', wintypes.DWORD)
    ]

def get_monitors_with_dpi():
    monitors = []
    def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        if ctypes.windll.user32.GetMonitorInfoW(hMonitor, ctypes.byref(info)):
            # 取得 DPI 縮放因子
            try:
                # Windows 8.1+ 支援 GetDpiForMonitor
                shcore = ctypes.windll.shcore
                dpiX = ctypes.c_uint()
                dpiY = ctypes.c_uint()
                shcore.GetDpiForMonitor(hMonitor, 0, ctypes.byref(dpiX), ctypes.byref(dpiY))
                scale_factor = dpiX.value / 96.0  # 96 DPI 是 100% 縮放
                
                # 計算原始解析度
                actual_width = info.rcMonitor.right - info.rcMonitor.left
                actual_height = info.rcMonitor.bottom - info.rcMonitor.top
                logical_width = int(actual_width / scale_factor)
                logical_height = int(actual_height / scale_factor)
                
                monitors.append({
                    'left': info.rcMonitor.left,
                    'top': info.rcMonitor.top,
                    'right': info.rcMonitor.right,
                    'bottom': info.rcMonitor.bottom,
                    'actual_width': actual_width,
                    'actual_height': actual_height,
                    'logical_width': logical_width,
                    'logical_height': logical_height,
                    'is_primary': bool(info.dwFlags & 1),
                    'scale_factor': scale_factor,
                    'dpi': dpiX.value
                })
            except Exception as e:
                print(f"  DPI 檢測失敗: {e}")
                monitors.append({
                    'left': info.rcMonitor.left,
                    'top': info.rcMonitor.top,
                    'right': info.rcMonitor.right,
                    'bottom': info.rcMonitor.bottom,
                    'actual_width': info.rcMonitor.right - info.rcMonitor.left,
                    'actual_height': info.rcMonitor.bottom - info.rcMonitor.top,
                    'logical_width': info.rcMonitor.right - info.rcMonitor.left,
                    'logical_height': info.rcMonitor.bottom - info.rcMonitor.top,
                    'is_primary': bool(info.dwFlags & 1),
                    'scale_factor': 1.0,
                    'dpi': 96
                })
        return True
    
    MONITORENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(wintypes.RECT), ctypes.c_ulong)
    ctypes.windll.user32.EnumDisplayMonitors(None, None, MONITORENUMPROC(callback), 0)
    return monitors

monitors_dpi = get_monitors_with_dpi()
for i, monitor in enumerate(monitors_dpi):
    print(f"\n螢幕 {i} (Windows API):")
    print(f"  位置: ({monitor['left']}, {monitor['top']})")
    print(f"  實際尺寸: {monitor['actual_width']} x {monitor['actual_height']}")
    print(f"  邏輯尺寸: {monitor['logical_width']} x {monitor['logical_height']}")
    print(f"  DPI: {monitor['dpi']}")
    print(f"  縮放比例: {monitor['scale_factor']:.2f}")
    print(f"  是否主螢幕: {monitor['is_primary']}")

# 檢查系統 DPI 設定
try:
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # 隱藏視窗
    
    # 取得系統 DPI
    system_dpi = root.winfo_fpixels('1i')
    print(f"\n系統 DPI: {system_dpi}")
    print(f"系統縮放比例: {system_dpi / 96:.2f}")
    
    root.destroy()
except Exception as e:
    print(f"\n無法取得系統 DPI: {e}")
