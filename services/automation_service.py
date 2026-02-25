import time
import os
import requests
from typing import Any, Dict, Optional, List
from gologin import GoLogin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, timedelta
from config.settings import GOLOGIN_TOKEN


class AutomationService:
    def __init__(
        self,
        profile_id,
        port,
        delay,
        videos_per_day,
        schedule_slots,
        video_paths,
        token=GOLOGIN_TOKEN,
        logger=None,
    ):
        self.token = token
        self.profile_id = profile_id
        self.port = port
        self.delay = delay
        self.videos_per_day = videos_per_day
        self.schedule_slots = schedule_slots
        self.video_paths = video_paths
        self.logger = logger

    def find_running_chrome_port(self):
        """
        Tìm Chrome DevTools port đang chạy.
        """
        # chỉ check port self.port
        try:
            endpoint = f"http://127.0.0.1:{self.port}/json/version"
            resp = requests.get(endpoint, timeout=0.2)
            if resp.ok:
                print(f"Tìm thấy!")
                return self.port
        except:
            return None

    def start_gologin_profile(self) -> Dict[str, Any]:
        """
        Khởi động hoặc attach vào GoLogin profile.
        """
        try:
            gl = GoLogin(
                {
                    "token": self.token,
                    "profile_id": self.profile_id,
                    "port": self.port,
                }
            )

            print("→ Tìm kiếm Chrome đang chạy...")
            existing_port = self.find_running_chrome_port()

            if existing_port:
                print(f"✓ Tìm thấy Chrome đang chạy trên port: {existing_port}")
                try:
                    self.wait_for_debug_port()
                    print("✓ Sử dụng lại Chrome đang chạy")
                    return {
                        "debug_port": str(existing_port),
                        "host": "127.0.0.1",
                        "gl_instance": gl,
                    }
                except:
                    print("→ Port không phản hồi, khởi động profile mới...")

            print("→ Khởi động profile mới...")
            debugger_address = gl.start()
            if not debugger_address:
                raise RuntimeError(
                    f"Không thể khởi động GoLogin cho Profile: {self.profile_id}"
                )

            host, port = str(debugger_address).split(":")
            print(f"✓ Đã khởi động profile mới trên port: {port}")
            return {"debug_port": port, "host": host, "gl_instance": gl}
        except Exception as e:
            raise RuntimeError(f"Lỗi khởi động GoLogin: {str(e)}")

    def find(self, driver, xpath, timeout=20):
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )

    def wait_for_debug_port(self) -> None:
        deadline = time.time() + 20
        endpoint = f"http://127.0.0.1:{self.port}/json/version"
        while time.time() < deadline:
            try:
                resp = requests.get(endpoint, timeout=3)
                if resp.ok:
                    return
            except Exception:
                pass
            time.sleep(0.7)
        raise RuntimeError(f"DevTools trên {self.port} không phản hồi.")

    def attach_selenium_to_gologin(self) -> webdriver.Chrome:
        chrome_options = Options()
        chrome_options.add_experimental_option(
            "debuggerAddress", f"127.0.0.1:{self.port}"
        )

        print(f"--- Đang tải ChromeDriver tương thích với Orbit 142... ---")
        try:
            service = Service(
                ChromeDriverManager(driver_version="142.0.7444.175").install()
            )
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception:
            print(f"Thử lại với phiên bản 142 tổng quát...")
            service = Service(ChromeDriverManager(driver_version="142").install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

        return driver

    def run_task(self):
        if not self.profile_id:
            if self.logger:
                self.logger("❌ Lỗi: Profile ID không được để trống")
            return

        if self.logger:
            self.logger(f"✓ Đang khởi tạo luồng chạy cho profile: {self.profile_id}")

        try:
            # 1. Start GoLogin
            profile_data = self.start_gologin_profile()
            debug_port = profile_data["debug_port"]
            gl_instance = profile_data["gl_instance"]

            # 2. Wait Port
            self.wait_for_debug_port()

            # 3. Connect Selenium
            driver = self.attach_selenium_to_gologin()
            if self.logger:
                self.logger(f"✓ Đã kết nối Selenium (Port {self.port})")

            # --- AUTOMATION LOGIC ---
            driver.get("https://business.facebook.com/latest/home")

            # Example Logic from app.py
            # Note: Just keeping structure here. In a real integration, we might want to pass more specialized params.

            # 1. Click "More"
            xpath_more = "//div[@role='button' and .//div[text()='More']]"
            if self.logger:
                self.logger("Đang tìm nút More...")
            self.find(driver, xpath_more).click()

            # 2. Click "Bulk upload reels"
            xpath_bulk = "//div[@role='menuitem' and contains(., 'Bulk upload reels')]"
            if self.logger:
                self.logger("Đang tìm nút Bulk upload reels...")
            self.find(driver, xpath_bulk).click()

            # 3. Upload videos - TẤT CẢ CÙNG LÚC
            if not self.video_paths:
                if self.logger:
                    self.logger("⚠️ Không có video nào để upload")
                return
            
            if self.logger:
                self.logger(f"Đang upload {len(self.video_paths)} video...")
            
            try:
                # Tìm input file
                xpath_input = "//input[@type='file' and contains(@accept, 'video')]"
                file_input = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, xpath_input))
                )
                
                # Gửi TẤT CẢ video paths cùng lúc (cách nhau bởi \n)
                all_paths = "\n".join([v.get("path") for v in self.video_paths])
                file_input.send_keys(all_paths)
                
                if self.logger:
                    self.logger(f"✓ Đã gửi {len(self.video_paths)} video")
                
                # Chờ tất cả upload 100%
                time.sleep(5)
                
                # Đợi cho đến khi có đủ số video hiển thị 100%
                for idx in range(len(self.video_paths)):
                    try:
                        WebDriverWait(driver, 180).until(
                            EC.presence_of_element_located((By.XPATH, f"(//*[contains(text(),'100%') or contains(text(),'Hoàn tất')])[{idx+1}]"))
                        )
                        if self.logger:
                            self.logger(f"✓ Video {idx+1}/{len(self.video_paths)} hoàn tất")
                    except Exception as e:
                        if self.logger:
                            self.logger(f"⚠ Timeout chờ video {idx+1}: {e}")
                        break
                
                time.sleep(3)
                
            except Exception as e:
                if self.logger:
                    self.logger(f"❌ Lỗi upload: {e}")
                return

            # 4. Schedule each video
            for i, video_item in enumerate(self.video_paths):

                # video_item keys: path, datetime, format
                target_dt = video_item.get("datetime")
                target_fmt = video_item.get("format", "AM")
                video_path = video_item.get("path")
                
                # Lấy tên file
                import os
                video_name = os.path.basename(video_path)
                video_name_no_ext = os.path.splitext(video_name)[0]

                print(f"[{i+1}/{len(self.video_paths)}] Scheduling: {video_name_no_ext}")

                print("Đang mở menu Publish...")
                # Tìm nút có chứa text 'Publish now'
                # Note: This strategy assumes the UI focus is on the current video or handles sequence
                # For Bulk Upload, you usually edit attributes for each row.
                # Assuming user's xpath works for the current context.
                xpath_publish_menu = (
                    "//div[@role='button' and .//div[contains(text(), 'Publish now')]]"
                )
                self.find(driver, xpath_publish_menu).click()

                # 5. Select Schedule
                print("Đang chọn Schedule...")
                xpath_schedule_option = (
                    "//div[@role='button' and .//div[contains(text(), 'Schedule')]]"
                )
                self.find(driver, xpath_schedule_option).click()

                # 6. Set Date
                # Format theo placeholder mm/dd/yyyy
                date_str = target_dt.strftime("%m/%d/%Y")

                print(f"Đang set lịch: {date_str}...")
                xpath_date_input = "//input[@placeholder='mm/dd/yyyy']"

                # 1. Click để focus vào ô input
                self.find(driver, xpath_date_input).click()
                time.sleep(1)

                # 2. Dùng ActionChains: Navigations từng phần
                actions = ActionChains(driver)

                # Loại bỏ số 0 ở đầu nếu tháng/ngày chỉ có 1 chữ số
                mm = str(target_dt.month)
                dd = str(target_dt.day)
                yyyy = target_dt.strftime("%Y")

                # Lấy giá trị hiện tại của input
                date_input = self.find(driver, xpath_date_input)
                current_value = date_input.get_attribute("value")
                print(f"Giá trị hiện tại của input: {current_value}")

                # Phân tích giá trị hiện tại để biết số ký tự cần xoá
                parts = current_value.split("/")
                if len(parts) == 3:
                    old_mm, old_dd, old_yyyy = parts
                    mm_delete_count = len(old_mm)
                    dd_delete_count = len(old_dd)
                    yyyy_delete_count = len(old_yyyy)
                else:
                    # Nếu không parse được, dùng mặc định
                    mm_delete_count = 2
                    dd_delete_count = 2
                    yyyy_delete_count = 4

                print(
                    f"Số ký tự cần xoá - Tháng: {mm_delete_count}, Ngày: {dd_delete_count}, Năm: {yyyy_delete_count}"
                )

                # 1. Về đầu (Tháng)
                print("→ Đang di chuyển về đầu input (HOME)...")
                actions.send_keys(Keys.HOME).perform()

                # Xoá tháng cũ theo số ký tự thực tế -> Nhập tháng mới
                for _ in range(mm_delete_count):
                    actions.send_keys(Keys.DELETE).perform()
                print(f"→ Đang nhập tháng mới: {mm}")
                actions.send_keys(mm).perform()

                # 2. Sang phải (qua dấu /) để đến Ngày
                print("→ Đang di chuyển sang phải đến phần ngày...")
                actions.send_keys(Keys.ARROW_RIGHT).perform()

                # Xoá ngày cũ theo số ký tự thực tế -> Nhập ngày mới
                for _ in range(dd_delete_count):
                    actions.send_keys(Keys.DELETE).perform()
                print(f"→ Đang nhập ngày mới: {dd}")
                actions.send_keys(dd).perform()

                # 3. Sang phải (qua dấu /) để đến Năm
                # (Logic năm cũ commented out theo code user, giữ nguyên nếu user muốn)

                print(f"✓ Đã set lịch: {mm}/{dd}/{yyyy}")

                # 4. Set giờ
                # Convert 24h sang 12h format
                hour_24 = target_dt.hour
                if hour_24 == 0:
                    target_hour_12 = "12"
                    target_fmt = "AM"
                elif hour_24 < 12:
                    target_hour_12 = str(hour_24)
                    target_fmt = "AM"
                elif hour_24 == 12:
                    target_hour_12 = "12"
                    target_fmt = "PM"
                else:
                    target_hour_12 = str(hour_24 - 12)
                    target_fmt = "PM"
                
                target_minute = target_dt.strftime("%M")

                print(f"\n→ Đang set giờ phút {target_hour_12}:{target_minute} {target_fmt}...")
                time.sleep(0.5)

                # Click vào input giờ
                xpath_hours = "//input[@aria-label='hours' and @role='spinbutton']"
                print("→ Đang click vào ô giờ...")
                hours_input = driver.find_element(By.XPATH, xpath_hours)
                hours_input.click()

                # Xoá giá trị cũ và nhập giờ mới
                hours_input.send_keys(Keys.CONTROL + "a")  # Select all
                hours_input.send_keys(target_hour_12)

                # 5. Set phút
                xpath_minutes = "//input[@aria-label='minutes' and @role='spinbutton']"
                print("→ Đang click vào ô phút...")
                minutes_input = driver.find_element(By.XPATH, xpath_minutes)
                minutes_input.click()

                # Xoá giá trị cũ và nhập phút mới
                minutes_input.send_keys(Keys.CONTROL + "a")  # Select all
                minutes_input.send_keys(target_minute)

                # 6. Set AM/PM
                xpath_meridiem = (
                    "//input[@aria-label='meridiem' and @role='spinbutton']"
                )
                print("→ Đang click vào ô AM/PM...")
                meridiem_input = driver.find_element(By.XPATH, xpath_meridiem)
                meridiem_input.click()

                # Kiểm tra giá trị hiện tại và thay đổi nếu cần
                current_meridiem = meridiem_input.get_attribute("aria-valuetext")
                print(f"→ AM/PM hiện tại: {current_meridiem}, Mục tiêu: {target_fmt}")

                if current_meridiem != target_fmt:
                    key_to_send = target_fmt.lower()[0]  # 'a' or 'p'
                    meridiem_input.send_keys(key_to_send)
                    print(f"→ Đã nhấn '{key_to_send}' để chuyển đổi")
                else:
                    print("→ Đã đúng định dạng")

                time.sleep(0.5)
                print(f"✓ Hoàn tất set lịch cho video {i+1}")

                # tiếp

            if self.logger:
                self.logger("✓ Task hoàn thành (Logic đang được chuyển đổi)")

        except Exception as e:
            if self.logger:
                self.logger(f"❌ Lỗi thực thi: {e}")
            print(f"Error: {e}")
        finally:
            # Cleanup if needed
            print("Finished automation task")
