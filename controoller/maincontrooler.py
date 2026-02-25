import threading
import time
import json
import os
import tkinter.messagebox as messagebox
from tkinter import filedialog
# from services.automation_service import AutomationService


class MainController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.project = self.main_window.project
        self.config_path = "temp/page_config.json"

        # State
        self.pages = []
        self.current_page_index = 0

        # Bind callbacks
        self.main_window.on_import_videos = self.import_videos
        self.main_window.on_delete_video = self.delete_video
        self.main_window.on_run_automation = self.run_automation
        self.main_window.on_generate_port = self.generate_random_port
        self.main_window.on_save_config = self.save_configuration
        self.main_window.on_add_page = self.add_page
        self.main_window.on_select_page = self.select_page
        self.main_window.on_delete_page = self.delete_page
        self.main_window.on_rename_page = self.rename_page
        self.main_window.on_add_videos = self.add_videos

        # Load initial data
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if isinstance(data, list):
                    self.pages = data
                elif isinstance(data, dict):
                    # Migrate legacy single config to list
                    data["page_name"] = "Default Page"
                    self.pages = [data]
                else:
                    self.pages = []

                # Migration: if "sidebar_name" exists but "page_name" doesn't, rename it
                # Remove "campaign_name" if present
                for p in self.pages:
                    if "sidebar_name" in p and "page_name" not in p:
                        p["page_name"] = p["sidebar_name"]
                        del p["sidebar_name"]
                    if "campaign_name" in p:
                        # If page_name is empty, use campaign_name
                        if not p.get("page_name"):
                            p["page_name"] = p["campaign_name"]
                        del p["campaign_name"]

            except Exception as e:
                print(f"Config load error: {e}")
                self.pages = []
        else:
            self.pages = []

        # Ensure at least one page exists
        if not self.pages:
            self.pages.append({
                "page_name": "Page 1",
                "command_line": "",
                "port": "",
                "delay": "0",
                "videos_per_day": "5",
                "schedule_slots": [],
                "note": ""
            })

        # Update UI
        self._refresh_sidebar()
        self.select_page(self.pages[0])

    def add_page(self, name):
        new_page = {
            "page_name": name,
            "command_line": "",
            "port": "",
            "delay": "0",
            "videos_per_day": "5",
            "schedule_slots": [],
            "note": ""
        }
        self.pages.append(new_page)
        self.save_persistent_config()

        self._refresh_sidebar(active_name=name)
        self.select_page(new_page)

    def select_page(self, page_data):
        if page_data in self.pages:
            self.current_page_index = self.pages.index(page_data)
            self.main_window.set_configuration(page_data)

            # Load History
            history = page_data.get("history", [])
            self.main_window.display_history(history)

            self._refresh_sidebar(active_name=page_data.get("page_name"))

    def delete_page(self):
        if not self.pages:
            return

        current_page = self.pages[self.current_page_index]
        name = current_page.get("page_name", "Unknown")

        confirm = messagebox.askyesno(
            "Xác nhận xoá", f"Bạn có chắc chắn muốn xoá page: {name}?")
        if not confirm:
            return

        # Remove
        self.pages.pop(self.current_page_index)

        # If empty, create default
        if not self.pages:
            self.pages.append({
                "page_name": "Page 1",
                "command_line": "",
                "profile_path": "",
                "port": "",
                "delay": "0",
                "videos_per_day": "5",
                "schedule_slots": [],
                "note": "",
                "history": []
            })

        # Adjust index if out of bounds
        if self.current_page_index >= len(self.pages):
            self.current_page_index = len(self.pages) - 1

        # Select new current
        new_current = self.pages[self.current_page_index]
        self._refresh_sidebar(active_name=new_current.get("page_name"))
        self.select_page(new_current)

        # Determine log vs show_message. Since this is a destructuve action, maybe just log or nothing.
        # User asked for delete button.
        self.save_persistent_config()
        self.main_window.log(f"Đã xoá page: {name}")

    def rename_page(self, new_name):
        """Đổi tên page đang được chọn"""
        if not self.pages:
            return
        
        current_page = self.pages[self.current_page_index]
        old_name = current_page.get("page_name", "Unknown")
        
        # Check trùng tên
        for p in self.pages:
            if p != current_page and p.get("page_name") == new_name:
                messagebox.showwarning("Trùng tên", f"Đã tồn tại page với tên: {new_name}")
                return
        
        # Đổi tên
        current_page["page_name"] = new_name
        
        # Cập nhật UI
        self._refresh_sidebar(active_name=new_name)
        self.main_window.set_configuration(current_page)
        
        # Lưu config
        self.save_persistent_config()
        self.main_window.log(f"✏️ Đã đổi tên page: {old_name} → {new_name}")

    def _refresh_sidebar(self, active_name=None):
        if hasattr(self.main_window, 'refresh_sidebar_pages'):
            self.main_window.refresh_sidebar_pages(
                self.pages, active_page_name=active_name)

    def generate_random_port(self):
        import random
        return str(random.randint(10000, 65535))

    def import_videos(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Video files", "*.mp4 *.mov *.avi")])
        if files:
            self.add_videos(files)

    def add_videos(self, files):
        # Kiểm tra Tab đang active
        active_tab = ""
        try:
            active_tab = self.main_window.video_tabview.get()
        except:
            pass
            
        if "Phần 2" in active_tab:
            # Xử lý nhập video cho chế độ Đăng Ngay
            for f in files:
                self.project.add_video(f)
                self.main_window.add_video_item_part2(f)
            self.main_window.update_status(f"✓ Đã thêm {len(files)} video vào Phần 2")
            return

        # ==========================================
        # XỬ LÝ NHẬP VIDEO CHO PHẦN 1 (LÊN LỊCH)
        # ==========================================
        # 1. Get current config context
        current_page = self.pages[self.current_page_index]
        
        # 2. Lấy pattern đã lưu (nếu có)
        saved_pattern = current_page.get("schedule_pattern")
        
        # 3. Lấy video hiện có
        existing_videos = self.main_window.get_video_items_data()
        
        # 4. Nếu đã có >= 5 video, học pattern từ 5 video đầu
        if len(existing_videos) >= 5:
            pattern = self._learn_pattern_from_first_n(existing_videos, 5)
            current_page["schedule_pattern"] = pattern
            self.save_persistent_config()
            self.main_window.log(f"📚 Đã học pattern từ 5 video đầu tiên")
        elif saved_pattern:
            pattern = saved_pattern
            self.main_window.log(f"📋 Dùng pattern đã lưu")
        else:
            # Chưa có pattern, dùng mặc định
            pattern = self._get_default_pattern()
            self.main_window.log(f"📋 Dùng pattern mặc định: 2 PM → 3 AM")
        
        # 5. Tính toán lịch cho video mới
        from datetime import datetime, timedelta
        
        # Bắt đầu từ HÔM NAY (thay vì ngày mai)
        start_date = datetime.now()
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Nếu đã có video, bắt đầu từ sau video cuối
        if existing_videos:
            last_video = existing_videos[-1]
            try:
                last_date = datetime.strptime(last_video["date"], "%m/%d/%Y")
                last_time = last_video["time"]
                last_ampm = last_video["ampm"]
                
                # Parse time
                if ":" in last_time:
                    hh, mm = map(int, last_time.split(":"))
                    if last_ampm == "PM" and hh != 12:
                        hh += 12
                    elif last_ampm == "AM" and hh == 12:
                        hh = 0
                    
                    last_datetime = last_date.replace(hour=hh, minute=mm)
                    
                    # Bắt đầu từ sau video cuối (cộng thêm 1 slot)
                    start_date = last_datetime
                    self.main_window.log(f"📅 Tiếp tục từ: {start_date.strftime('%d/%m/%Y %H:%M')}")
            except Exception as e:
                self.main_window.log(f"⚠ Lỗi parse video cuối: {e}")
        
        # 6. Áp dụng pattern cho video mới
        current_count = len(existing_videos)
        
        for i, f in enumerate(files):
            global_idx = current_count + i
            
            # Tính ngày và giờ theo pattern
            schedule_info = self._calculate_schedule_from_pattern(pattern, global_idx, start_date)
            
            date_str = schedule_info["date"]
            time_str = schedule_info["time"]
            ampm_str = schedule_info["ampm"]
            
            # Add to Project
            self.project.add_video(f)
            
            # Add to UI
            self.main_window.add_video_item(f, date_str, time_str, ampm_str)
        
        self.main_window.update_status(f"✓ Đã nạp thêm {len(files)} video vào Phần 1")
    
    def _learn_pattern_from_first_n(self, videos, n=5):
        """
        Học pattern từ N video đầu tiên
        Phân tích theo NGÀY: Ngày nào có bao nhiêu video, giờ nào, AM/PM
        """
        from datetime import datetime
        from collections import defaultdict
        
        # Chỉ lấy N video đầu
        sample_videos = videos[:n]
        
        # Group by date (theo thứ tự)
        by_date = {}
        date_order = []
        
        for v in sample_videos:
            date = v["date"]
            if date not in by_date:
                by_date[date] = []
                date_order.append(date)
            
            time = v["time"]
            ampm = v["ampm"]
            by_date[date].append({"time": time, "ampm": ampm})
        
        # Phân tích pattern theo NGÀY
        cycles = []
        for date in date_order:
            videos_in_day = by_date[date]
            
            # Lấy AM/PM chủ đạo của ngày
            am_count = sum(1 for v in videos_in_day if v["ampm"] == "AM")
            pm_count = sum(1 for v in videos_in_day if v["ampm"] == "PM")
            
            period = "PM" if pm_count >= am_count else "AM"
            
            # Lấy times (giữ nguyên format 12h)
            times = [v["time"] for v in videos_in_day]
            
            cycles.append({
                "count": len(videos_in_day),
                "period": period,
                "times": times,
                "day_offset": len(cycles)  # Ngày thứ mấy trong pattern
            })
        
        if not cycles:
            return self._get_default_pattern()
        
        return {
            "type": "learned",
            "cycles": cycles,
            "learned_from": n,
            "days_per_cycle": len(cycles)  # Số ngày trong 1 chu kỳ
        }
    
    def _get_default_pattern(self):
        """
        Pattern mặc định: 
        - Ngày 1: 3 video PM
        - Ngày 2: 2 video AM
        - Lặp lại...
        """
        return {
            "type": "default",
            "cycles": [
                {"count": 3, "period": "PM", "times": ["06:00", "08:00", "10:00"], "day_offset": 0},
                {"count": 2, "period": "AM", "times": ["09:00", "11:00"], "day_offset": 1}
            ],
            "days_per_cycle": 2
        }
    
    def _calculate_schedule_from_pattern(self, pattern, video_index, start_date):
        """
        Tính toán lịch cho video thứ video_index theo pattern
        Mỗi cycle = 1 NGÀY
        """
        from datetime import datetime, timedelta
        
        cycles = pattern["cycles"]
        days_per_cycle = pattern.get("days_per_cycle", len(cycles))
        
        # Tính tổng video trong 1 chu kỳ (tất cả các ngày)
        total_videos_per_cycle = sum(c["count"] for c in cycles)
        
        # Xác định chu kỳ thứ mấy (mỗi chu kỳ = days_per_cycle ngày)
        cycle_number = video_index // total_videos_per_cycle
        
        # Vị trí trong chu kỳ hiện tại
        position_in_cycle = video_index % total_videos_per_cycle
        
        # Tìm ngày (cycle) và vị trí trong ngày đó
        videos_counted = 0
        day_index = 0
        position_in_day = 0
        
        for i, cycle in enumerate(cycles):
            if position_in_cycle < videos_counted + cycle["count"]:
                day_index = i
                position_in_day = position_in_cycle - videos_counted
                break
            videos_counted += cycle["count"]
        
        current_cycle = cycles[day_index]
        
        # Tính ngày thực tế - FIX: Dùng day_offset từ cycle thay vì day_index
        # Mỗi chu kỳ lặp lại = days_per_cycle ngày
        # Ngày thực tế = start_date + (cycle_number * days_per_cycle) + day_offset_in_pattern
        day_offset_in_pattern = current_cycle.get("day_offset", day_index)
        total_days_offset = cycle_number * days_per_cycle + day_offset_in_pattern
        target_date = start_date + timedelta(days=total_days_offset)
        
        # Lấy time từ cycle
        times = current_cycle["times"]
        if position_in_day < len(times):
            time_str = times[position_in_day]
        else:
            # Fallback: lặp lại times
            time_str = times[position_in_day % len(times)] if times else "12:00"
        
        # Xác định AM/PM
        ampm = current_cycle["period"]
        
        # Parse time (đã là 12h format rồi)
        if ":" not in time_str:
            time_str = "12:00"
        
        return {
            "date": target_date.strftime("%m/%d/%Y"),
            "time": time_str,
            "ampm": ampm
        }

    def delete_video(self, path):
        self.project.remove_video(path)
        self.main_window.update_status(
            f"Hàng đợi: {len(self.project.video_items)} video")

    def run_automation(self):
        self.main_window.set_processing_state(True)
        threading.Thread(target=self._automation_task, daemon=True).start()

    def _automation_task(self):
        from datetime import datetime, timedelta

        # Get data
        current_page = self.pages[self.current_page_index]
        schedule_slots = current_page.get("schedule_slots", [])
        use_api = current_page.get("use_api", False)

        # Get Videos directly from UI to respect user's manual edits
        ui_videos_data = self.main_window.get_video_items_data()
        # Format: [{"path":..., "date": "mm/dd/yyyy", "time": "hh:mm", "ampm": "AM/PM"}]

        payload_videos = []

        for item in ui_videos_data:
            try:
                # Parse date
                d_str = item["date"]
                t_str = item["time"]
                ampm = item["ampm"]

                # Parse date: mm/dd/yyyy
                dt_date = datetime.strptime(d_str, "%m/%d/%Y")

                # Parse time: hh:mm (12h format)
                if ":" in t_str:
                    hh, mm = map(int, t_str.split(":"))
                else:
                    hh, mm = 12, 0
                
                # Convert 12h to 24h format
                if ampm == "PM":
                    if hh != 12:
                        hh += 12
                elif ampm == "AM":
                    if hh == 12:
                        hh = 0

                final_dt = dt_date.replace(hour=hh, minute=mm, second=0)

                payload_videos.append({
                    "path": item["path"],
                    "datetime": final_dt,
                    "format": ampm
                })
            except Exception as e:
                print(f"Skipping video {item['path']} due to parse error: {e}")
                continue
        
        ui_videos_data_p2 = self.main_window.get_video_part2_data()
        for item in ui_videos_data_p2:
            payload_videos.append({
                "path": item["path"],
                "is_part2": True # Đánh dấu là chế độ Đăng Ngay
            })

        print("Payload:", payload_videos)

        try:
            if use_api:
                # Use Facebook Graph API
                from services.fb_graph_api_service import FacebookGraphAPIService
                
                page_id = current_page.get("page_id", "")
                access_token = current_page.get("access_token", "")
                
                if not page_id or not access_token:
                    self.main_window.log("❌ Thiếu Page ID hoặc Access Token!")
                    self.main_window.set_processing_state(False)
                    return
                
                self.main_window.log("🚀 Starting Facebook Graph API...")
                
                service = FacebookGraphAPIService(
                    page_id=page_id,
                    access_token=access_token,
                    video_paths=payload_videos,
                    logger=self.main_window.log
                )
                
                # Test connection first
                if not service.test_connection():
                    self.main_window.log("❌ Không kết nối được API. Kiểm tra Page ID và Access Token!")
                    self.main_window.set_processing_state(False)
                    return
                
                service.run_task()
                self.main_window.log("✓ API process finished.")
            else:
                # Use Selenium (Chrome) - Phiên bản cải tiến
                from services.chrome_stealth_service import ChromeStealthService
                self.main_window.log("🚀 Starting Chrome Automation (Stealth Mode)...")
                
                binary_location = current_page.get("binary_location", current_page.get("profile_id", ""))
                profile_path = current_page.get("profile_path", "")
                command_line = current_page.get("command_line", "")
                page_id = current_page.get("page_id", "")
                
                service = ChromeStealthService(
                    command_line=command_line,
                    binary_location=binary_location,
                    profile_path=profile_path,
                    video_paths=payload_videos,
                    logger=self.main_window.log,
                    page_id=page_id
                )
                service.run_task()
                
                self.main_window.log("✓ Chrome process finished.")
        except Exception as e:
            self.main_window.log(f"❌ Error during automation: {e}")
            print(f"Automation Error: {e}")

        # Note: Previous AutomationService.run_task call removed as requested.

        # Update History if successful (Approximation: if we got here without exception from run_task)
        if "history" not in current_page:
            current_page["history"] = []

        for item in payload_videos:
            import os
            fname = os.path.basename(item["path"])
            dt_obj = item["datetime"]  # datetime object

            hist_item = {
                "video_name": fname,
                "time_str": dt_obj.strftime("%H:%M %p"),
                "date_str": dt_obj.strftime("%d/%m/%Y"),
                "timestamp": dt_obj.timestamp(),
                "status": "Scheduled"
            }
            current_page["history"].append(hist_item)

        # Save updated history
        self.save_persistent_config()

        # Update UI (Must be on main thread, but tkinter handles some threading.
        # Safest to use after via lambda if strict, but methods here are direct calls).
        # We can re-select page to refresh history
        self.main_window.after(
            0, lambda: self.main_window.display_history(current_page["history"]))

        self.main_window.set_processing_state(False)
        self.main_window.show_message(
            "Hoàn thành", "Automation kết thúc (check log).")

    def save_configuration(self, data):
        # Parse command line automation
        cmd = data.get("command_line", "").strip()
        if cmd:
            import re
            # Extract Binary (start of string)
            # Handles "C:\Path\..." or C:\Path\...
            exe_match = re.match(r'^"?([^"]+\.exe)"?', cmd, re.IGNORECASE)
            if exe_match:
                data['binary_location'] = exe_match.group(1)
            
            # Extract User Data Dir
            # Handles --user-data-dir="C:\..." or --user-data-dir=C:\...
            # Note: The regex finds the value part looking for quotes or until space
            profile_match = re.search(r'--user-data-dir=["\']?([^"\']+)["\']?', cmd, re.IGNORECASE)
            if profile_match:
                # If the capture group ends with a quote due to greedy match, strip it?
                # The character class [^"']+ should avoid matching the closing quote if present inside?
                # Actually, simpler: search for --user-data-dir="([^"]+)" OR --user-data-dir=([^\s]+)
                
                # Robust extraction:
                p_val = profile_match.group(1)
                # If parsing failed to stop at quote, cleanup might be needed, but [^"'] works for quoted content usually.
                data['profile_path'] = p_val
            
            print(f"Parsed Config -> Binary: {data.get('binary_location')}, Profile: {data.get('profile_path')}")


        # Update current page data
        current_page = self.pages[self.current_page_index]
        current_page.update(data)
        
        # AUTO-SAVE: Học pattern từ 5 video đầu (nếu có)
        existing_videos = self.main_window.get_video_items_data()
        if len(existing_videos) >= 5:
            pattern = self._learn_pattern_from_first_n(existing_videos, 5)
            current_page["schedule_pattern"] = pattern
            self.main_window.log(f"💾 Đã học pattern từ 5 video đầu tiên")
        elif len(existing_videos) > 0:
            # Ít hơn 5 video, vẫn học nhưng cảnh báo
            pattern = self._learn_pattern_from_first_n(existing_videos, len(existing_videos))
            current_page["schedule_pattern"] = pattern
            self.main_window.log(f"💾 Đã học pattern từ {len(existing_videos)} video (khuyến nghị >= 5)")

        self.save_persistent_config()
        page_name = current_page.get("page_name", "")

        # Refresh sidebar in case name changed
        self._refresh_sidebar(active_name=page_name)
        
        # Reload calendar to reflect updated videos_per_day setting
        history = current_page.get("history", [])
        self.main_window.display_history(history)

        self.main_window.log(
            f"Đã lưu cấu hình thành công cho page: {page_name}")
            
        # Re-select page to refresh UI fields (showing parsed binary/profile)
        self.select_page(current_page)


    def save_persistent_config(self):
        try:
            os.makedirs("temp", exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.pages, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Save error: {e}")

    def cleanup(self):
        print("Cleaning up resources...")
        # Cleanup crawler controller if exists
        if hasattr(self, 'main_window') and hasattr(self.main_window, 'crawler_controller'):
            if self.main_window.crawler_controller:
                self.main_window.crawler_controller.cleanup()
