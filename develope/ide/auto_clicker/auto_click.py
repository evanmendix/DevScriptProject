#!/usr/bin/env python3
"""
自動圖片識別點擊腳本
當螢幕上出現指定圖片時，自動點擊該圖片位置

使用方法:
1. 將目標圖片放入 target_images/ 目錄
2. 安裝需求套件: pip install -r requirements.txt
3. 執行 python auto_click.py
4. 按 Ctrl+C 停止腳本

多螢幕支援:
- 自動檢測所有連接的螢幕
- 顯示每個螢幕的位置、尺寸和主螢幕標識
- 支援跨螢幕的圖片識別和點擊

作者: Auto-generated
"""

import pyautogui
import time
import os
import sys
from pathlib import Path
import argparse
import re

try:
    import pyautogui._pyautogui_win as win
    HAS_MULTI_DISPLAY = True
except ImportError:
    HAS_MULTI_DISPLAY = False

# 嘗試導入其他多螢幕檢測方法
try:
    import screeninfo
    HAS_SCREENINFO = True
except ImportError:
    HAS_SCREENINFO = False

class AutoClicker:
    def __init__(self, target_dir="target_images", confidence=0.8, check_interval=3.0, screen_region=None, scroll_after_click=False, scroll_amount=3):
        """
        初始化自動點擊器
        
        Args:
            target_dir: 目標圖片目錄
            confidence: 圖片識別信心度 (0.0-1.0)
            check_interval: 檢查間隔時間（秒）
            screen_region: 螢幕檢查區域 (left, top, width, height)
            scroll_after_click: 點擊後是否滾輪滾動
            scroll_amount: 滾輪滾動量（正數向下，負數向上）
        """
        # 取得腳本所在目錄，確保相對路徑正確
        script_dir = Path(__file__).parent
        self.target_dir = script_dir / target_dir
        self.confidence = confidence
        self.check_interval = check_interval
        self.running = True
        self.scroll_after_click = scroll_after_click
        self.scroll_amount = scroll_amount
        
        # 設定 pyautogui 安全設定
        pyautogui.FAILSAFE = True  # 滑鼠移動到左上角時停止程式
        pyautogui.PAUSE = 0.05     # 每個操作後暫停 0.05 秒
        
        # 檢測並顯示螢幕資訊
        self.display_info = self.detect_displays()
        self.print_display_info()
        
        # 設定螢幕檢查區域
        if screen_region is None:
            # 使用新的螢幕選擇邏輯
            display_id = getattr(self, 'target_display_id', None)
            region_type = getattr(self, 'target_region_type', 'right_1_3')
            self.screen_region = self.get_screen_region_for_display(display_id, region_type)
            
            # 顯示使用的螢幕資訊
            if display_id is not None:
                print(f"DEBUG: 使用螢幕 {display_id} 的 {region_type} 區域: {self.screen_region}")
            else:
                print(f"DEBUG: 使用主螢幕的 {region_type} 區域: {self.screen_region}")
        else:
            self.screen_region = screen_region
        
        print(f"自動點擊器已啟動")
        print(f"目標圖片目錄: {self.target_dir.absolute()}")
        print(f"識別信心度: {self.confidence}")
        print(f"檢查間隔: {self.check_interval} 秒")
        print(f"檢查區域: 右方 2/3 螢幕 {self.screen_region}")
        if self.scroll_after_click:
            print(f"點擊後滾輪: 向下 {self.scroll_amount} 格")
        print(f"按 Ctrl+C 停止腳本")
        print("-" * 50)
        
    def load_target_images(self):
        """載入目標圖片列表"""
        if not self.target_dir.exists():
            print(f"目標圖片目錄不存在: {self.target_dir}")
            return []
            
        image_entries = []
        patterns = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif']
        for ext in patterns:
            image_entries.extend(
                {
                    "path": img,
                    "confidence": self.extract_confidence_from_path(img),
                    "click_ratio": self.extract_click_ratio_from_path(img)
                }
                for img in self.target_dir.rglob(ext)
            )
            
        if not image_entries:
            print(f"在 {self.target_dir} 中沒有找到圖片檔案")
            print("請將目標圖片放入該目錄中 (支援 .png, .jpg, .jpeg, .bmp, .gif)")
            return []
            
        print(f"找到 {len(image_entries)} 個目標圖片:")
        for entry in image_entries:
            confidence_info = (
                f" (指定信心度: {entry['confidence']})"
                if entry["confidence"] is not None else ""
            )
            click_ratio_info = (
                f" (點擊比例: X={entry['click_ratio'][0]*100:.0f}% Y={entry['click_ratio'][1]*100:.0f}%)"
                if entry["click_ratio"] is not None else ""
            )
            print(
                f"   - {entry['path'].relative_to(self.target_dir)}"
                f"{confidence_info}{click_ratio_info}"
            )
        print()
        
        return image_entries

    def extract_confidence_from_path(self, image_path: Path):
        """從目錄名稱推導圖片信心度設定"""
        try:
            relative_parts = image_path.relative_to(self.target_dir).parts[:-1]
        except ValueError:
            # 圖片不在 target_dir 中
            return None
        pattern = re.compile(r"conf(?:idence)?[_-]?([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE)
        for part in relative_parts:
            match = pattern.match(part)
            if not match:
                continue
            value = float(match.group(1))
            if value > 1:
                value /= 100
            return max(0.0, min(value, 1.0))
        return None
    
    def extract_click_ratio_from_path(self, image_path: Path):
        """從目錄名稱推導圖片點擊比例設定 (X/Y 介於 0-1)"""
        try:
            relative_parts = image_path.relative_to(self.target_dir).parts[:-1]
        except ValueError:
            return None
        pattern = re.compile(
            r"click[_-]?x([0-9]+(?:\.[0-9]+)?)[_-]?y([0-9]+(?:\.[0-9]+)?)",
            re.IGNORECASE
        )
        for part in relative_parts:
            match = pattern.search(part)
            if not match:
                continue
            x_val = float(match.group(1))
            y_val = float(match.group(2))
            if x_val > 1:
                x_val /= 100
            if y_val > 1:
                y_val /= 100
            return (
                max(0.0, min(x_val, 1.0)),
                max(0.0, min(y_val, 1.0))
            )
        return None
    
    def get_screen_region_for_display(self, display_id=None, region_type="right_2_3"):
        """
        取得指定螢幕的檢查區域
        
        Args:
            display_id: 螢幕 ID (None 表示主螢幕)
            region_type: 區域類型 ("right_2_3", "bottom_right", "full", etc.)
        
        Returns:
            tuple: (left, top, width, height)
        """
        if display_id is None:
            # 找出主螢幕
            for display in self.display_info:
                if display['is_primary']:
                    target_display = display
                    break
            else:
                # 如果沒有主螢幕，使用第一個
                target_display = self.display_info[0] if self.display_info else None
        else:
            # 使用指定的螢幕
            target_display = None
            for display in self.display_info:
                if display['id'] == display_id:
                    target_display = display
                    break
        
        if not target_display:
            # 回退到整個畫布
            screen_width, screen_height = pyautogui.size()
            return (screen_width // 3, 0, screen_width - screen_width // 3, screen_height)
        
        left = target_display['left']
        top = target_display['top']
        width = target_display['width']
        height = target_display['height']
        
        if region_type == "right_1_3":
            # 右側 1/3
            region_left = left + (width // 3 * 2)
            region_top = top
            region_width = width // 3
            region_height = height
        elif region_type == "right_2_3":
            # 右側 2/3
            region_left = left + (width // 3)
            region_top = top
            region_width = width - (width // 3)
            region_height = height
        elif region_type == "bottom_right":
            # 右下角 1/3
            region_left = left + (width // 3 * 2)
            region_top = top + (height // 3 * 2)
            region_width = width // 3
            region_height = height // 3
        elif region_type == "right_bottom_third":
            # 右下角 (右側 1/3 + 下方 1/2)
            region_left = left + (width // 3 * 2)
            region_top = top + (height // 2)
            region_width = width // 3
            region_height = height // 2
        elif region_type == "bottom_right_quarter":
            # 右下角 1/4
            region_left = left + (width // 2)
            region_top = top + (height // 2)
            region_width = width // 2
            region_height = height // 2
        elif region_type == "bottom_half":
            # 下半部
            region_left = left
            region_top = top + (height // 2)
            region_width = width
            region_height = height // 2
        else:  # "full"
            # 整個螢幕
            region_left = left
            region_top = top
            region_width = width
            region_height = height
        
        return (region_left, region_top, region_width, region_height)
    
    def get_dpi_info(self):
        try:
            import ctypes
            from ctypes import wintypes
            
            class MONITORINFO(ctypes.Structure):
                _fields_ = [
                    ('cbSize', wintypes.DWORD),
                    ('rcMonitor', wintypes.RECT),
                    ('rcWork', wintypes.RECT),
                    ('dwFlags', wintypes.DWORD)
                ]
            
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
                        
                        # 計算實際解析度
                        actual_width = info.rcMonitor.right - info.rcMonitor.left
                        actual_height = info.rcMonitor.bottom - info.rcMonitor.top
                        logical_width = int(actual_width / scale_factor)
                        logical_height = int(actual_height / scale_factor)
                        
                        monitors.append({
                            'left': info.rcMonitor.left,
                            'top': info.rcMonitor.top,
                            'actual_width': actual_width,
                            'actual_height': actual_height,
                            'logical_width': logical_width,
                            'logical_height': logical_height,
                            'is_primary': bool(info.dwFlags & 1),
                            'scale_factor': scale_factor,
                            'dpi': dpiX.value
                        })
                    except Exception:
                        # 如果無法取得 DPI，使用預設值
                        actual_width = info.rcMonitor.right - info.rcMonitor.left
                        actual_height = info.rcMonitor.bottom - info.rcMonitor.top
                        monitors.append({
                            'left': info.rcMonitor.left,
                            'top': info.rcMonitor.top,
                            'actual_width': actual_width,
                            'actual_height': actual_height,
                            'logical_width': actual_width,
                            'logical_height': actual_height,
                            'is_primary': bool(info.dwFlags & 1),
                            'scale_factor': 1.0,
                            'dpi': 96
                        })
                return True
            
            MONITORENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(wintypes.RECT), ctypes.c_ulong)
            ctypes.windll.user32.EnumDisplayMonitors(None, None, MONITORENUMPROC(callback), 0)
            return monitors
        except Exception as e:
            print(f"無法取得 DPI 資訊: {e}")
            return []
    
    def detect_displays(self):
        """檢測所有螢幕並回傳資訊"""
        displays = []
        
        # 強制使用 screeninfo 函式庫，並修正 DPI 縮放問題
        if HAS_SCREENINFO:
            try:
                monitors = screeninfo.get_monitors()
                print(f"DEBUG: screeninfo 找到 {len(monitors)} 個螢幕")
                
                # 使用 Windows API 取得正確的 DPI 縮放資訊
                dpi_info = self.get_dpi_info()
                
                for i, monitor in enumerate(monitors):
                    print(f"DEBUG: 螢幕 {i} - {monitor.name}: {monitor.width}x{monitor.height} at ({monitor.x}, {monitor.y})")
                    
                    # 檢查是否需要 DPI 修正
                    actual_width = monitor.width
                    actual_height = monitor.height
                    
                    # 如果有 DPI 資訊，使用實際尺寸
                    if i < len(dpi_info):
                        dpi_data = dpi_info[i]
                        if dpi_data['scale_factor'] != 1.0:
                            # 使用實際尺寸（物理像素）
                            actual_width = dpi_data['actual_width']
                            actual_height = dpi_data['actual_height']
                            print(f"DEBUG: DPI 修正 - 系統報告尺寸: {actual_width}x{actual_height}, 縮放: {dpi_data['scale_factor']:.2f}")
                    
                    displays.append({
                        'id': i,
                        'name': monitor.name or f'螢幕 {i+1}',
                        'left': monitor.x,
                        'top': monitor.y,
                        'width': actual_width,
                        'height': actual_height,
                        'is_primary': monitor.is_primary,
                        'logical_width': monitor.width,
                        'logical_height': monitor.height,
                        'scale_factor': dpi_info[i]['scale_factor'] if i < len(dpi_info) else 1.0
                    })
                return displays
            except Exception as e:
                print(f"screeninfo 檢測失敗: {e}")
        
        # 如果 screeninfo 失敗，才嘗試其他方法
        print("DEBUG: screeninfo 不可用，嘗試其他方法")
        
        # 嘗試使用 pyautogui 的內建方法
        if HAS_MULTI_DISPLAY:
            try:
                # 使用 pyautogui 的所有螢幕尺寸方法
                try:
                    # 嘗試取得所有螢幕資訊
                    all_screens = pyautogui._pyautogui_win.getAllScreens()
                    if all_screens and len(all_screens) > 1:
                        for i, screen in enumerate(all_screens):
                            displays.append({
                                'id': i,
                                'name': f'螢幕 {i+1}',
                                'left': screen['left'],
                                'top': screen['top'],
                                'width': screen['width'],
                                'height': screen['height'],
                                'is_primary': screen.get('is_primary', i == 0)
                            })
                        return displays
                except (AttributeError, TypeError):
                    pass
                
                # 嘗試其他方法
                try:
                    # 使用 Windows API 透過 ctypes，包含 DPI 感知
                    import ctypes
                    from ctypes import wintypes
                    
                    class MONITORINFO(ctypes.Structure):
                        _fields_ = [
                            ('cbSize', wintypes.DWORD),
                            ('rcMonitor', wintypes.RECT),
                            ('rcWork', wintypes.RECT),
                            ('dwFlags', wintypes.DWORD)
                        ]
                    
                    def get_monitors():
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
                                except:
                                    scale_factor = 1.0
                                
                                monitors.append({
                                    'left': info.rcMonitor.left,
                                    'top': info.rcMonitor.top,
                                    'right': info.rcMonitor.right,
                                    'bottom': info.rcMonitor.bottom,
                                    'width': info.rcMonitor.right - info.rcMonitor.left,
                                    'height': info.rcMonitor.bottom - info.rcMonitor.top,
                                    'is_primary': bool(info.dwFlags & 1),  # MONITORINFOF_PRIMARY
                                    'scale_factor': scale_factor
                                })
                            return True
                        
                        MONITORENUMPROC = ctypes.WINFUNCTYPE(ctypes.BOOL, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(wintypes.RECT), ctypes.c_ulong)
                        ctypes.windll.user32.EnumDisplayMonitors(None, None, MONITORENUMPROC(callback), 0)
                        return monitors
                    
                    monitors = get_monitors()
                    for i, monitor in enumerate(monitors):
                        displays.append({
                            'id': i,
                            'name': f'螢幕 {i+1}',
                            'left': monitor['left'],
                            'top': monitor['top'],
                            'width': monitor['width'],
                            'height': monitor['height'],
                            'is_primary': monitor['is_primary'],
                            'scale_factor': monitor.get('scale_factor', 1.0)
                        })
                    return displays
                    
                except Exception as e:
                    print(f"Windows API 檢測失敗: {e}")
                    
            except Exception as e:
                print(f"無法取得詳細螢幕資訊: {e}")
        
        # 回退到基本方法
        width, height = pyautogui.size()
        displays.append({
            'id': 0,
            'name': '主要螢幕',
            'left': 0,
            'top': 0,
            'width': width,
            'height': height,
            'is_primary': True
        })
        
        return displays
    
    def print_display_info(self):
        """顯示螢幕資訊"""
        print(f"檢測到 {len(self.display_info)} 個螢幕:")
        print("-" * 40)
        
        for display in self.display_info:
            primary_mark = " (主螢幕)" if display['is_primary'] else ""
            print(f"   {display['id']}: {display['name']}{primary_mark}")
            print(f"      位置: ({display['left']}, {display['top']})")
            
            # 檢查是否有 DPI 縮放資訊
            if 'scale_factor' in display and display['scale_factor'] != 1.0:
                print(f"      邏輯尺寸: {display['logical_width']} x {display['logical_height']}")
                print(f"      系統報告尺寸: {display['width']} x {display['height']}")
                print(f"      DPI 縮放比例: {display['scale_factor']:.2f}")
            elif 'raw_width' in display and 'raw_height' in display:
                if display['raw_width'] != display['width'] or display['raw_height'] != display['height']:
                    print(f"      原始尺寸: {display['raw_width']} x {display['raw_height']}")
                    print(f"      系統報告尺寸: {display['width']} x {display['height']}")
                    scale_x = display['width'] / display['raw_width']
                    scale_y = display['height'] / display['raw_height']
                    print(f"      縮放比例: X={scale_x:.2f} Y={scale_y:.2f}")
                else:
                    print(f"      尺寸: {display['width']} x {display['height']}")
            else:
                print(f"      尺寸: {display['width']} x {display['height']}")
            
            print(f"      範圍: ({display['left']}, {display['top']}) - ({display['left'] + display['width']}, {display['top'] + display['height']})")
            print()
        
        # 計算總螢幕區域
        if len(self.display_info) > 1:
            min_left = min(d['left'] for d in self.display_info)
            min_top = min(d['top'] for d in self.display_info)
            max_right = max(d['left'] + d['width'] for d in self.display_info)
            max_bottom = max(d['top'] + d['height'] for d in self.display_info)
            total_width = max_right - min_left
            total_height = max_bottom - min_top
            
            print(f"總螢幕區域: {total_width} x {total_height}")
            print(f"   起始位置: ({min_left}, {min_top})")
            print(f"   結束位置: ({max_right}, {max_bottom})")
            print("-" * 40)
    
    def find_and_click_image(self, image_path, custom_confidence=None, click_ratio=None):
        """
        尋找並點擊指定圖片
        
        Args:
            image_path: 圖片路徑
            custom_confidence: 自訂信心度（覆蓋預設值）
            click_ratio: (x_ratio, y_ratio) 介於 0-1 的相對點擊位置
            
        Returns:
            bool: 是否成功找到並點擊
        """
        try:
            # 使用自訂信心度或預設信心度
            confidence = custom_confidence if custom_confidence is not None else self.confidence
            if click_ratio is None:
                click_ratio = (0.5, 0.5)
            x_ratio = max(0.0, min(click_ratio[0], 1.0))
            y_ratio = max(0.0, min(click_ratio[1], 1.0))
            
            # 在指定螢幕區域內尋找圖片
            location = pyautogui.locateOnScreen(
                str(image_path), 
                confidence=confidence,
                region=self.screen_region  # 限制檢查區域
            )
            
            if location:
                # 依照指定比例計算點擊位置
                x = int(location.left + location.width * x_ratio)
                y = int(location.top + location.height * y_ratio)
                
                # 顯示更詳細的識別資訊
                print(f"✅ 找到圖片 {image_path.name} 在位置 ({x}, {y})")
                print(f"   圖片尺寸: {location.width}x{location.height}")
                print(f"   信心度設定: {confidence}")
                print(f"   點擊比例: X={x_ratio*100:.1f}% Y={y_ratio*100:.1f}%")
                
                # 除錯模式：截圖並標記識別區域
                if hasattr(self, 'debug_mode') and self.debug_mode:
                    self.debug_screenshot(location, image_path.name)
                
                # 直接點擊圖片位置，不移動滑鼠
                pyautogui.click(x, y)
                
                # 點擊後滾輪滾動
                if self.scroll_after_click:
                    pyautogui.scroll(self.scroll_amount)
                    print(f"已向下滾動 {self.scroll_amount} 格")
                
                print(f"已點擊位置 ({x}, {y})")
                return True
            else:
                return False
                
        except pyautogui.ImageNotFoundException:
            return False
        except Exception as e:
            print(f"處理圖片 {image_path.name} 時發生錯誤: {e}")
            return False
    
    def run(self):
        """執行自動點擊主循環"""
        target_images = self.load_target_images()
        
        if not target_images:
            print("❌ 沒有可用的目標圖片，程式結束")
            return
        
        click_count = 0
        start_time = time.time()
        
        try:
            while self.running:
                found_any = False
                
                # 檢查每個目標圖片
                for image_entry in target_images:
                    image_path = image_entry["path"]
                    # 依目錄配置信心度，若無則維持原有啟發式
                    custom_confidence = image_entry.get("confidence")
                    if custom_confidence is None:
                        if "scroll_down" in image_path.name.lower():
                            custom_confidence = 0.7
                        elif "antigravity_start" in image_path.name.lower():
                            custom_confidence = 0.6
                    click_ratio = image_entry.get("click_ratio")
                    
                    if self.find_and_click_image(image_path, custom_confidence, click_ratio):
                        click_count += 1
                        found_any = True
                        # 點擊後稍作等待，避免重複點擊
                        time.sleep(0.2)
                        break  # 找到一個就重新開始檢查
                
                if not found_any:
                    # 沒找到任何圖片，等待下次檢查
                    time.sleep(self.check_interval)
                else:
                    print(f"📊 總點擊次數: {click_count} | 運行時間: {int(time.time() - start_time)}秒")
                    
        except KeyboardInterrupt:
            print("\n🛑 使用者中斷，程式結束")
        finally:
            print(f"📈 最終統計: 總共點擊 {click_count} 次，運行 {int(time.time() - start_time)} 秒")
    
    def test_mode(self):
        """測試模式：截圖並檢查識別結果"""
        target_images = self.load_target_images()
        
        if not target_images:
            print("❌ 沒有可用的目標圖片，程式結束")
            return
        
        print("測試模式：檢查識別結果（不會實際點擊）")
        print("=" * 50)
        
        # 截圖
        screenshot = pyautogui.screenshot()
        screenshot_path = "test_screenshot.png"
        screenshot.save(screenshot_path)
        print(f"已截圖並儲存為: {screenshot_path}")
        
        for entry in target_images:
            image_path = entry["path"]
            print(f"\n檢查圖片: {image_path.name}")
            
            try:
                # 嘗試不同信心度
                for confidence in [0.9, 0.8, 0.7, 0.6]:
                    try:
                        location = pyautogui.locateOnScreen(
                            str(image_path), 
                            confidence=confidence,
                            region=self.screen_region  # 限制檢查區域
                        )
                        
                        if location:
                            center = pyautogui.center(location)
                            print(f"   [信心度 {confidence}]: 找到在位置 ({center.x}, {center.y})")
                            print(f"   [尺寸]: {location.width}x{location.height}")
                            break
                        else:
                            print(f"   [信心度 {confidence}]: 未找到")
                    except pyautogui.ImageNotFoundException:
                        print(f"   [信心度 {confidence}]: 未找到")
                        
            except Exception as e:
                print(f"   [錯誤]: {e}")
        
        print(f"\n提示: 您可以查看截圖 {screenshot_path} 來確認螢幕內容")
    
    def debug_detailed_analysis(self, image_path):
        """詳細除錯分析：找出所有可能的匹配位置"""
        try:
            import cv2
            import numpy as np
            
            # 讀取目標圖片
            target_img = cv2.imread(str(image_path))
            target_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
            
            # 截圖
            screenshot = pyautogui.screenshot()
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            screenshot_gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
            
            # 限制檢查區域
            left, top, width, height = self.screen_region
            region = screenshot_gray[top:top+height, left:left+width]
            
            print(f"🔍 詳細分析圖片: {image_path.name}")
            print(f"   目標圖片尺寸: {target_img.shape[1]}x{target_img.shape[0]}")
            print(f"   檢查區域: {width}x{height}")
            
            # 嘗試不同匹配方法
            methods = ['cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF_NORMED']
            
            for method_name in methods:
                method = eval(method_name)
                result = cv2.matchTemplate(region, target_gray, method)
                
                if method == cv2.TM_SQDIFF_NORMED:
                    locations = np.where(result <= 0.3)  # SQDIFF 越小越好
                else:
                    locations = np.where(result >= 0.7)  # 其他方法越大越好
                
                if len(locations[0]) > 0:
                    print(f"   ✅ {method_name}: 找到 {len(locations[0])} 個可能匹配")
                    
                    # 顯示前3個最佳匹配位置
                    for i in range(min(3, len(locations[0]))):
                        y, x = locations[0][i], locations[1][i]
                        confidence = result[y, x] if method != cv2.TM_SQDIFF_NORMED else 1 - result[y, x]
                        print(f"      位置 {i+1}: ({left+x}, {top+y}) 信心度: {confidence:.3f}")
                else:
                    print(f"   ❌ {method_name}: 無匹配")
            
        except ImportError:
            print("   ⚠️  需要安裝 opencv-python 進行詳細分析")
        except Exception as e:
            print(f"   ❌ 分析失敗: {e}")

def main():
    """主程式入口"""
    parser = argparse.ArgumentParser(description="自動圖片識別點擊腳本")
    parser.add_argument(
        "--target-dir", 
        default="target_images",
        help="目標圖片目錄 (預設: target_images)"
    )
    parser.add_argument(
        "--confidence", 
        type=float, 
        default=0.8,
        help="圖片識別信心度 0.0-1.0 (預設: 0.8)"
    )
    parser.add_argument(
        "--interval", 
        type=float, 
        default=3.0,
        help="檢查間隔時間（秒）(預設: 3.0)"
    )
    parser.add_argument(
        "--region",
        type=str,
        help="螢幕檢查區域，格式: left,top,width,height (預設: 右方 2/3)"
    )
    parser.add_argument(
        "--scroll",
        action="store_true",
        help="點擊後滾輪向下滾動"
    )
    parser.add_argument(
        "--scroll-amount",
        type=int,
        default=3,
        help="滾輪滾動量（預設: 3 格向下）"
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="測試模式：截圖並檢查識別結果，不實際點擊"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="詳細分析模式：分析所有可能的匹配位置"
    )
    parser.add_argument(
        "--display",
        type=int,
        help="指定要檢查的螢幕 ID (0=第一個螢幕, 1=第二個螢幕, 等等)"
    )
    parser.add_argument(
        "--region-type",
        type=str,
        choices=["right_1_3", "right_2_3", "right_bottom_third", "bottom_right", "bottom_right_quarter", "bottom_half", "full"],
        default="right_1_3",
        help="螢幕檢查區域類型 (預設: right_1_3)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="除錯模式：儲存標記識別區域的截圖"
    )
    
    args = parser.parse_args()
    
    # 驗證參數
    if not 0.0 <= args.confidence <= 1.0:
        print("❌ 信心度必須在 0.0 到 1.0 之間")
        sys.exit(1)
    
    if args.interval <= 0:
        print("❌ 檢查間隔時間必須大於 0")
        sys.exit(1)
    
    # 解析螢幕區域參數
    screen_region = None
    if args.region:
        try:
            region_parts = [int(x.strip()) for x in args.region.split(',')]
            if len(region_parts) != 4:
                raise ValueError("區域參數需要 4 個數值")
            screen_region = tuple(region_parts)
        except ValueError as e:
            print(f"❌ 區域參數格式錯誤: {e}")
            print("正確格式: left,top,width,height")
            sys.exit(1)
    
    # 建立並執行自動點擊器
    clicker = AutoClicker(
        target_dir=args.target_dir,
        confidence=args.confidence,
        check_interval=args.interval,
        screen_region=screen_region,
        scroll_after_click=args.scroll,
        scroll_amount=args.scroll_amount
    )
    
    # 設定螢幕目標
    clicker.target_display_id = args.display
    clicker.target_region_type = args.region_type
    
    # 重新計算螢幕區域（如果指定了螢幕參數）
    if args.display is not None or args.region_type != "right_1_3":
        clicker.screen_region = clicker.get_screen_region_for_display(args.display, args.region_type)
        if args.display is not None:
            print(f"指定螢幕 {args.display} 的 {args.region_type} 區域: {clicker.screen_region}")
        else:
            print(f"主螢幕的 {args.region_type} 區域: {clicker.screen_region}")
    
    # 設定除錯模式
    if args.debug:
        clicker.debug_mode = True
    
    if args.test_mode:
        clicker.test_mode()
    elif args.analyze:
        # 詳細分析模式
        target_images = clicker.load_target_images()
        if target_images:
            for entry in target_images:
                clicker.debug_detailed_analysis(entry["path"])
    else:
        clicker.run()

if __name__ == "__main__":
    main()
