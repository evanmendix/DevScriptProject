#!/usr/bin/env python3
import screeninfo

print("測試 screeninfo 函式庫:")
monitors = screeninfo.get_monitors()

for i, monitor in enumerate(monitors):
    print(f"\n螢幕 {i}:")
    print(f"  名稱: {monitor.name}")
    print(f"  位置: ({monitor.x}, {monitor.y})")
    print(f"  尺寸: {monitor.width} x {monitor.height}")
    print(f"  是否主螢幕: {monitor.is_primary}")
    
    # 檢查所有屬性
    print(f"  所有屬性: {dir(monitor)}")
    
    # 檢查是否有 scale 屬性
    if hasattr(monitor, 'scale'):
        print(f"  縮放比例: {monitor.scale}")
    else:
        print("  沒有 scale 屬性")
