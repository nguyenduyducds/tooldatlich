import time
import os
import re
from datetime import datetime
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

class ChromeAttackService:
    def __init__(self, command_line, binary_location, profile_path, video_paths, logger):
        self.command_line = command_line
        self.binary_location = binary_location
        self.profile_path = profile_path
        self.video_paths = video_paths
        self.logger = logger
        self.driver = None
        self.wait = None

    def run_task(self):
        self.logger("Initializing Chrome Driver...")

        try:
            extra_args = []
            if self.command_line:
                p_match = re.search(r'--proxy-server=([^\s]+)', self.command_line)
                if p_match:
                    extra_args.append(f"--proxy-server={p_match.group(1)}")

                keys = ["--gologing_proxy_server_username", "--gologing_proxy_server_password"]
                for k in keys:
                    match = re.search(rf'{k}=([^\s]+)', self.command_line)
                    if match:
                        extra_args.append(f"{k}={match.group(1)}")

            self.driver = Driver(
                uc=False,
                binary_location=self.binary_location,
                user_data_dir=self.profile_path,
                chromium_arg=" ".join(extra_args) if extra_args else None,
                headless=False
            )
            self.wait = WebDriverWait(self.driver, 90)

            self.logger("Browser Launched. Navigating to Bulk Composer...")
            self.driver.get("https://business.facebook.com/latest/bulk_upload_composer?asset_id=906358839234021")
            time.sleep(8)

            if not self.video_paths:
                self.logger("No videos in queue!")
                return

            processed_count = 0

            for video in self.video_paths:
                path = video['path']
                dt = video['datetime']

                video_name = os.path.basename(path)
                video_name_no_ext = os.path.splitext(video_name)[0]
                self.logger(f"Processing: {video_name}")

                try:
                    # 1. Upload
                    file_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
                    file_input.send_keys(path)
                    self.logger(f"Sent file: {video_name}")

                    # 2. Chờ upload 100%
                    self.wait.until(EC.presence_of_element_located((By.XPATH, "(//*[contains(text(),'100%') or contains(text(),'Hoàn tất')])[last()]")))
                    self.logger("Upload hoàn tất 100%")
                    time.sleep(3)

                    # 2.5. Chờ kiểm tra bản quyền hoàn tất
                    self.logger("Đang chờ kiểm tra bản quyền...")
                    copyright_check_done = False
                    max_wait = 120  # Chờ tối đa 2 phút
                    start_time = time.time()
                    
                    while not copyright_check_done and (time.time() - start_time) < max_wait:
                        try:
                            # Kiểm tra xem có đang kiểm tra bản quyền không
                            checking_elements = self.driver.find_elements(By.XPATH, 
                                "//*[contains(text(), 'Đang kiểm tra') or contains(text(), 'kiểm tra bản quyền') or contains(text(), 'Checking')]")
                            
                            if not checking_elements:
                                # Không còn thông báo "Đang kiểm tra" -> đã xong
                                copyright_check_done = True
                                self.logger("Kiểm tra bản quyền hoàn tất!")
                            else:
                                time.sleep(2)  # Chờ 2s rồi check lại
                        except:
                            # Nếu không tìm thấy element nào -> coi như đã xong
                            copyright_check_done = True
                    
                    if not copyright_check_done:
                        self.logger("Timeout chờ kiểm tra bản quyền, tiếp tục...")
                    
                    time.sleep(2)  # Chờ thêm chút để UI ổn định

                    # 3. Đọc Tiêu đề từ cột "Tiêu đề" để copy sang "Mô tả"
                    self.logger("📋 Đang đọc nội dung từ cột Tiêu đề...")
                    caption_text = video_name_no_ext  # fallback
                    
                    try:
                        # Facebook tự động điền Tiêu đề vào dropdown, cần lấy text hiển thị
                        # Tìm element chứa tiêu đề trong cột "Tiêu đề"
                        title_xpaths = [
                            # Dropdown button text (visible text)
                            "(//div[contains(@role, 'button')]//span[string-length(text()) > 5])[last()]",
                            # Input text nếu vẫn còn
                            "(//input[@type='text' and not(contains(@placeholder, 'ngày')) and not(contains(@placeholder, 'giờ'))])[last()]"
                        ]
                        
                        for idx, xpath in enumerate(title_xpaths):
                            try:
                                title_elements = self.driver.find_elements(By.XPATH, xpath)
                                if title_elements:
                                    title_el = title_elements[-1]
                                    # Thử lấy value (nếu là input) hoặc text (nếu là span/div)
                                    current_title = self.driver.execute_script("return arguments[0].value || arguments[0].textContent;", title_el) or ""
                                    current_title = current_title.strip()
                                    
                                    if current_title and len(current_title) > 3:
                                        caption_text = current_title
                                        self.logger(f"✓ Đọc được Tiêu đề (chiến lược #{idx+1}): '{caption_text}'")
                                        break
                            except Exception as e:
                                self.logger(f"  Chiến lược #{idx+1} thất bại: {e}")
                                continue
                        
                        if caption_text == video_name_no_ext:
                            self.logger("⚠ Không đọc được Tiêu đề từ UI, dùng tên file")
                    except Exception as e:
                        self.logger(f"❌ Lỗi đọc Tiêu đề: {e}, dùng tên file")

                    # 4. Copy Tiêu đề sang Mô tả - Click vào cột Mô tả để mở editor
                    self.logger(f"📝 Đang copy Tiêu đề sang Mô tả: '{caption_text}'")
                    
                    try:
                        # Bước 1: Tìm và click vào cột "Mô tả" để mở editor
                        desc_trigger = None
                        
                        # Chiến lược 1: Tìm div có text placeholder chứa "Mô tả"
                        try:
                            desc_triggers = self.driver.find_elements(By.XPATH, 
                                "//*[contains(text(), 'thuộc phim') or contains(text(), 'Mô tả')]")
                            if desc_triggers:
                                desc_trigger = desc_triggers[-1]  # Lấy cái cuối (row mới nhất)
                                self.logger(f"  ✓ Tìm thấy cột Mô tả (chiến lược #1)")
                        except:
                            pass
                        
                        # Chiến lược 2: Tìm div có role textbox
                        if not desc_trigger:
                            try:
                                desc_triggers = self.driver.find_elements(By.XPATH, 
                                    "//div[contains(@role, 'textbox') or contains(@contenteditable, 'true')]//div[contains(text(), 'Mô tả')]")
                                if desc_triggers:
                                    desc_trigger = desc_triggers[-1]
                                    self.logger(f"  ✓ Tìm thấy cột Mô tả (chiến lược #2)")
                            except:
                                pass
                        
                        if not desc_trigger:
                            self.logger("❌ Không tìm thấy cột Mô tả để click!")
                        else:
                            # Scroll vào view
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", desc_trigger)
                            time.sleep(1)
                            
                            # Highlight để debug
                            self.driver.execute_script("""
                                arguments[0].style.border = '3px solid blue';
                                arguments[0].style.backgroundColor = 'lightblue';
                            """, desc_trigger)
                            time.sleep(0.5)
                            
                            # Click để mở editor
                            self.logger("  📝 Click vào cột Mô tả để mở editor...")
                            desc_trigger.click()
                            time.sleep(2)
                            
                            # Remove highlight
                            self.driver.execute_script("""
                                arguments[0].style.border = '';
                                arguments[0].style.backgroundColor = '';
                            """, desc_trigger)
                        
                        # Bước 2: Tìm textarea trong popup/editor đã mở
                        time.sleep(1)
                        all_textareas = self.driver.find_elements(By.XPATH, "//textarea")
                        self.logger(f"Tìm thấy tổng cộng {len(all_textareas)} textarea sau khi click")
                        
                        desc_el = None
                        if all_textareas:
                            # Lấy textarea cuối cùng (vừa mở)
                            desc_el = all_textareas[-1]
                            placeholder = desc_el.get_attribute("placeholder") or "N/A"
                            self.logger(f"  ✓ Dùng textarea cuối (placeholder: '{placeholder}')")
                        
                        # Fallback: Tìm div contenteditable
                        if not desc_el:
                            try:
                                contenteditable_divs = self.driver.find_elements(By.XPATH, 
                                    "//div[@contenteditable='true' and not(contains(@aria-label, 'Tiêu đề'))]")
                                if contenteditable_divs:
                                    desc_el = contenteditable_divs[-1]
                                    self.logger(f"  ✓ Dùng div contenteditable")
                            except:
                                pass
                        
                        if desc_el:
                            # Scroll vào view
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", desc_el)
                            time.sleep(1)
                            
                            # Focus bằng nhiều cách
                            self.driver.execute_script("arguments[0].focus();", desc_el)
                            time.sleep(0.3)
                            desc_el.click()
                            time.sleep(0.5)
                            
                            # Clear triệt để
                            self.driver.execute_script("arguments[0].value = '';", desc_el)
                            time.sleep(0.2)
                            desc_el.clear()
                            time.sleep(0.3)
                            
                            # Điền từng ký tự để chắc chắn
                            desc_el.send_keys(caption_text)
                            time.sleep(1)
                            
                            # Trigger change event (quan trọng cho React/Vue)
                            self.driver.execute_script("""
                                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                            """, desc_el)
                            time.sleep(0.5)
                            
                            # Verify
                            current_value = self.driver.execute_script("return arguments[0].value;", desc_el)
                            self.logger(f"Giá trị sau khi điền: '{current_value}'")
                            
                            if current_value and caption_text in current_value:
                                self.logger(f"✓ Đã điền Mô tả thành công!")
                            else:
                                self.logger(f"⚠ Mô tả chưa điền đúng - Expected: '{caption_text}', Got: '{current_value}'")
                        else:
                            self.logger("❌ Không tìm thấy textarea/editor sau khi click!")
                    except Exception as e:
                        self.logger(f"❌ Lỗi điền Mô tả: {e}")
                        import traceback
                        self.logger(f"Traceback: {traceback.format_exc()}")

                    # 5. Đặt lịch SAU KHI đã điền Mô tả
                    try:
                        # Dropdown
                        sched_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "(//span[contains(., 'Đăng ngay') or contains(., 'Lựa chọn')])[last()]/ancestor::div[@role='button']")))
                        sched_btn.click()
                        self.logger("Mở dropdown lịch")
                        time.sleep(2)

                        # Tab Lên lịch
                        tab_el = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(., 'Lên lịch')]/ancestor::div[@role='tab' or @role='button' or contains(@class, 'tab')]")))
                        tab_el.click()
                        self.logger("Chọn tab 'Lên lịch'")
                        time.sleep(3)

                        date_str = dt.strftime("%d/%m/%Y")
                        time_str = dt.strftime("%H:%M")

                        # Ngày (dùng JS nếu send_keys fail)
                        try:
                            date_input = self.driver.find_element(By.XPATH, "//input[contains(@value, 'Tháng') or contains(@placeholder, 'ngày')][last()]")
                            self.driver.execute_script("arguments[0].value = arguments[1];", date_input, date_str)
                            self.logger(f"Ngày (JS): {date_str}")
                        except:
                            self.logger("Fail ngày bằng JS, thử send_keys")
                            date_input.click()
                            date_input.send_keys(Keys.CONTROL + "a" + Keys.BACKSPACE)
                            date_input.send_keys(date_str)

                        # Giờ
                        try:
                            time_input = self.driver.find_element(By.XPATH, "//input[contains(@value, ':') or contains(@placeholder, 'giờ')][last()]")
                            self.driver.execute_script("arguments[0].value = arguments[1];", time_input, time_str)
                            self.logger(f"Giờ (JS): {time_str}")
                        except:
                            self.logger("Fail giờ bằng JS, thử send_keys")
                            time_input.click()
                            time_input.send_keys(Keys.CONTROL + "a" + Keys.BACKSPACE)
                            time_input.send_keys(time_str)

                        # Cập nhật (retry 2 lần)
                        updated = False
                        for _ in range(2):
                            try:
                                update_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(., 'Cập nhật')]/ancestor::div[@role='button']")))
                                update_btn.click()
                                self.logger("Đã click 'Cập nhật'")
                                updated = True
                                time.sleep(4)
                                break
                            except:
                                time.sleep(2)
                        if not updated:
                            self.logger("Không click được 'Cập nhật' sau 2 lần thử")

                    except Exception as sched_e:
                        self.logger(f"Lỗi lịch: {sched_e}")

                    processed_count += 1
                    time.sleep(3)

                except Exception as e:
                    self.logger(f"Lỗi xử lý {video_name}: {e}")

            # Final Đăng - CHỜ TẤT CẢ VIDEO KIỂM TRA BẢN QUYỀN XONG
            self.logger("Đang kiểm tra trạng thái bản quyền tất cả video trước khi Đăng...")
            
            # Chờ tất cả video không còn "Đang kiểm tra"
            all_clear = False
            max_final_wait = 180  # Chờ tối đa 3 phút cho tất cả
            start_final = time.time()
            
            while not all_clear and (time.time() - start_final) < max_final_wait:
                try:
                    checking_elements = self.driver.find_elements(By.XPATH, 
                        "//*[contains(text(), 'Đang kiểm tra') or contains(text(), 'kiểm tra bản quyền') or contains(text(), 'Checking')]")
                    
                    if not checking_elements:
                        all_clear = True
                        self.logger("✓ Tất cả video đã kiểm tra bản quyền xong!")
                    else:
                        self.logger(f"Còn {len(checking_elements)} video đang kiểm tra bản quyền...")
                        time.sleep(5)  # Chờ 5s rồi check lại
                except:
                    all_clear = True
            
            if not all_clear:
                self.logger("⚠ Timeout chờ kiểm tra bản quyền, thử Đăng...")
            
            time.sleep(3)  # Chờ thêm để chắc chắn

            try:
                publish_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and contains(., 'Đăng') and not(contains(., 'ngay'))][last()]")))
                publish_btn.click()
                self.logger("✓ Đã nhấn ĐĂNG!")
            except:
                self.logger("❌ Không tìm thấy nút Đăng - kiểm tra thủ công!")

            self.logger(f"Hoàn thành {processed_count}/{len(self.video_paths)} video.")

        except Exception as e:
            self.logger(f"Lỗi nghiêm trọng: {e}")

        finally:
            self.logger("Task finished. Browser giữ mở.")