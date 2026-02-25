import time
import os
import re
from datetime import datetime
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class ChromeStealthService:
    """
    Service upload video lên Facebook với stealth mode
    Multilingual model: tự nhận diện ngôn ngữ Facebook
    """
    
    # ═══ MULTILINGUAL MODEL ═══
    # Keywords cho mỗi action, cover 12+ ngôn ngữ Facebook
    FB_LANG = {
        "publish": [
            "publish", "đăng ngay", "đăng", "i-publish", "publicar", "publier",
            "veröffentlichen", "pubblicare", "yayınla", "terbitkan", "เผยแพร่",
            "发布", "公開", "게시", "опубликовать", "publicera"
        ],
        "schedule": [
            "schedule", "i-schedule", "lên lịch", "lịch", "iskedyul", "programar",
            "programmer", "planen", "programmare", "zamanla", "jadwalkan", "ตั้งเวลา",
            "排期", "予約", "예약", "запланировать", "schemalägg"
        ],
        "update": [
            "update", "i-update", "cập nhật", "actualizar", "mettre à jour",
            "aktualisieren", "aggiornare", "güncelle", "perbarui", "อัปเดต",
            "更新", "업데이트", "обновить", "uppdatera"
        ],
        "save": [
            "save", "i-save", "lưu", "guardar", "enregistrer", "speichern",
            "salvare", "kaydet", "simpan", "บันทึก", "保存", "저장", "сохранить"
        ],
        "draft": [
            "draft", "nháp", "bilang draft", "borrador", "brouillon", "entwurf",
            "bozza", "taslak", "draf", "ฉบับร่าง", "草稿", "임시", "черновик"
        ],
        "date": [
            "date", "ngày", "petsa", "fecha", "datum", "data", "tarih", "tanggal",
            "วันที่", "日期", "날짜", "дата"
        ],
        "hours": [
            "hours", "giờ", "oras", "horas", "heures", "stunden", "ore", "saat",
            "jam", "ชั่วโมง", "小时", "時", "시간", "часы"
        ],
        "minutes": [
            "minutes", "phút", "minuto", "minutos", "stunde", "minuti", "dakika",
            "menit", "นาที", "分钟", "分", "분", "минуты"
        ],
        "months": [
            "enero", "pebrero", "marso", "abril", "mayo", "hunyo", "hulyo",
            "agosto", "setyembre", "oktubre", "nobyembre", "disyembre",
            "january", "february", "march", "april", "may", "june", "july",
            "august", "september", "october", "november", "december",
            "tháng", "januari", "februari", "maret", "mei", "juni", "juli",
            "agustus", "oktober", "desember"
        ]
    }
    
    def __init__(self, command_line, binary_location, profile_path, video_paths, logger, page_id=None):
        self.command_line = command_line
        self.binary_location = binary_location
        self.profile_path = profile_path
        self.video_paths = video_paths
        self.logger = logger
        self.page_id = page_id or ""  # Trống = sẽ auto-detect
        self.driver = None
        self.wait = None

    def run_task(self):
        self.logger("Initializing Chrome Driver...")

        try:
            extra_args = []
            if self.command_line:
                # Lấy TẤT CẢ arguments từ command line gốc (không chỉ proxy)
                # Bỏ qua các flag mà SeleniumBase tự thêm
                skip_flags = ['--force-device-scale-factor', '--start-maximized', '--window-size']
                
                # Parse tất cả --flag từ command line
                import shlex
                try:
                    parts = shlex.split(self.command_line)
                except:
                    parts = self.command_line.split()
                
                for part in parts:
                    if part.startswith('--') and not any(part.startswith(s) for s in skip_flags):
                        # Bỏ --user-data-dir vì đã truyền riêng
                        if not part.startswith('--user-data-dir'):
                            extra_args.append(part)
                
                self.logger(f"  Args: {len(extra_args)} flags từ command line")

            # XÓA CẤU HÌNH NHỎ ĐỂ ÉP FULL MÀN HÌNH TỪ CHROMIUM
            extra_args.append('--start-maximized')
            extra_args.append('--window-size=1920,1080')

            from seleniumbase import Driver
            self.driver = Driver(
                uc=False,
                binary_location=self.binary_location,
                user_data_dir=self.profile_path,
                chromium_arg=" ".join(extra_args) if extra_args else None,
                headless=False
            )
            
            # Ép hệ điều hành Windows phóng to cửa sổ của tiến trình Chrome đang hiển thị!
            # Bypass hoàn toàn các thông số khóa khung hình (Screen Resolution) của Antidetect Browser
            try:
                import ctypes
                import time
                time.sleep(1) # Chờ cho Chrome kịp bung hiển thị frame cửa sổ
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                if hwnd:
                    ctypes.windll.user32.ShowWindow(hwnd, 3) # 3: SW_MAXIMIZE
                
                # Double-check với thư viện Selenium Cổ Điển
                self.driver.maximize_window()
            except Exception as e:
                pass
            
            self.wait = WebDriverWait(self.driver, 90)

            self.logger(f"Browser Launched. Page ID: {self.page_id}")
            
            # Auto-detect Page ID nếu chưa có
            if not self.page_id:
                self.logger("🔍 Auto-detecting Page ID...")
                try:
                    self.driver.get("https://business.facebook.com/latest/home")
                    time.sleep(5)
                    
                    # Lấy Page ID từ URL redirect hoặc từ page context
                    detected_id = self.driver.execute_script("""
                        // Cách 1: Lấy từ URL hiện tại
                        const url = window.location.href;
                        const assetMatch = url.match(/asset_id=(\d+)/);
                        if (assetMatch) return assetMatch[1];
                        
                        // Cách 2: Lấy từ meta Business Suite context  
                        const links = document.querySelectorAll('a[href*="asset_id="]');
                        for (const link of links) {
                            const m = link.href.match(/asset_id=(\d+)/);
                            if (m) return m[1];
                        }
                        
                        // Cách 3: Lấy từ window context
                        if (window.__routeParams && window.__routeParams.asset_id) {
                            return window.__routeParams.asset_id;
                        }
                        
                        // Cách 4: Tìm trong tất cả script tags
                        const scripts = document.querySelectorAll('script');
                        for (const s of scripts) {
                            const text = s.textContent || '';
                            const pageMatch = text.match(/"pageID":"(\d+)"/);
                            if (pageMatch) return pageMatch[1];
                        }
                        
                        return null;
                    """)
                    
                    if detected_id:
                        self.page_id = detected_id
                        self.logger(f"  ✓ Detected Page ID: {self.page_id}")
                    else:
                        # Thử lấy từ URL hiện tại sau redirect
                        current_url = self.driver.current_url
                        import re as re2
                        url_match = re2.search(r'asset_id=(\d+)', current_url)
                        if url_match:
                            self.page_id = url_match.group(1)
                            self.logger(f"  ✓ Page ID from URL: {self.page_id}")
                        else:
                            self.logger("  ⚠ Không detect được Page ID. Vui lòng nhập thủ công trong Config!")
                            self.logger(f"  URL hiện tại: {current_url}")
                except Exception as e:
                    self.logger(f"  ⚠ Auto-detect lỗi: {e}")
            
            self.logger(f"Navigating to Bulk Composer (Page: {self.page_id})...")
            try:
                self.driver.maximize_window()
            except Exception as e:
                self.logger(f"  ⚠ Không thể maximize window: {e}")
            self.driver.get(f"https://business.facebook.com/latest/bulk_upload_composer?asset_id={self.page_id}")
            time.sleep(8)

            if not self.video_paths:
                self.logger("No videos in queue!")
                return

            # UPLOAD TẤT CẢ VIDEO CÙNG LÚC
            self.logger(f"📤 Đang upload {len(self.video_paths)} video cùng lúc...")
            try:
                file_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
                
                # Gửi TẤT CẢ video paths cùng lúc (cách nhau bởi \n)
                all_paths = "\n".join([v['path'] for v in self.video_paths])
                file_input.send_keys(all_paths)
                self.logger(f"✓ Đã gửi {len(self.video_paths)} video")
                
                # Bắt đầu chờ nền tảng nhận file (Ít nhất thoát khỏi trạng thái 0%)
                self.logger("  ⏳ Đang chờ hệ thống Facebook tiếp nhận Video (Trạng thái > 0%)...")
                
                # Loop tối đa 60 giây để chờ
                for _ in range(30):
                    time.sleep(2)
                    is_still_zero = self.driver.execute_script("""
                        var spans = document.querySelectorAll('span');
                        var zeroCount = 0;
                        for(var i=0; i<spans.length; i++) {
                            if(spans[i].textContent === '0%') {
                                zeroCount++;
                            }
                        }
                        // Nếu vẫn còn chữ số 0% đang hiển thị tương ứng với số video
                        return zeroCount > 0;
                    """)
                    
                    if not is_still_zero:
                        self.logger("  ✓ Video đã bắt đầu quá trình tải lên (Thoát ngưỡng 0%)")
                        break
                else:
                    self.logger("  ⚠ Thời gian chờ tiếp nhận quá lâu hoặc không tìm thấy thanh tiến trình, cứ tiếp tục...")
                
                # Chờ thêm 1 xíu để DOM Dropdown ổn định hẳn
                time.sleep(2)
                
            except Exception as e:
                self.logger(f"❌ Lỗi upload: {e}")
                return
            
            # Video đã upload qua UI → chỉ cần đặt lịch bằng Selenium
            # (Token internal từ browser không có quyền Graph API) 
            self.logger("📅 Đặt lịch cho từng video...")
            processed_count = self._schedule_via_selenium()
            
            self.logger(f"✅ Hoàn thành đặt lịch {processed_count}/{len(self.video_paths)} video.")
            self.logger("ℹ️ Người dùng tự kiểm tra và bấm 'Đăng' khi sẵn sàng.")

        except Exception as e:
            self.logger(f"Lỗi nghiêm trọng: {e}")

        finally:
            self.logger("Task finished. Browser giữ mở.")
    
    def _schedule_via_selenium(self):
        """
        Đặt lịch bằng JavaScript thuần chạy trong browser (siêu nhanh)
        Tất cả click/find đều dùng JS, chỉ Python sleep giữa các bước
        """
        processed_count = 0
        
        # Chờ UI render đầy đủ
        time.sleep(8)
        
        # DEBUG: Dump tất cả buttons trên trang để hiểu cấu trúc
        dom_debug = self.driver.execute_script("""
            var result = {buttons: [], selects: [], dropdowns: [], inputs: [], links: []};
            
            // Tất cả role=button
            var btns = document.querySelectorAll('[role="button"]');
            for (var i = 0; i < btns.length && i < 30; i++) {
                var t = (btns[i].textContent || '').trim().substring(0, 50);
                var hp = btns[i].getAttribute('aria-haspopup');
                var cls = (btns[i].className || '').substring(0, 60);
                result.buttons.push({text: t, haspopup: hp, tag: btns[i].tagName, cls: cls});
            }
            
            // Tất cả select elements
            var sels = document.querySelectorAll('select');
            for (var i = 0; i < sels.length; i++) {
                var opts = [];
                for (var j = 0; j < sels[i].options.length && j < 5; j++) {
                    opts.push(sels[i].options[j].text);
                }
                result.selects.push({opts: opts, name: sels[i].name});
            }
            
            // Tất cả elements có aria-haspopup
            var hps = document.querySelectorAll('[aria-haspopup]');
            for (var i = 0; i < hps.length; i++) {
                result.dropdowns.push({
                    tag: hps[i].tagName, 
                    text: (hps[i].textContent||'').trim().substring(0,40),
                    role: hps[i].getAttribute('role'),
                    hp: hps[i].getAttribute('aria-haspopup')
                });
            }
            
            // Div/span chứa text publish/schedule (đa ngôn ngữ)
            var pubWords = arguments[0]; var schedWords = arguments[1];
            var allEls = document.querySelectorAll('div, span, a');
            for (var i = 0; i < allEls.length; i++) {
                var t = (allEls[i].textContent || '').trim();
                if (t.length > 2 && t.length < 30) {
                    var tl = t.toLowerCase();
                    var match = false;
                    for (var w = 0; w < pubWords.length; w++) { if (tl.includes(pubWords[w])) { match = true; break; } }
                    if (!match) for (var w = 0; w < schedWords.length; w++) { if (tl.includes(schedWords[w])) { match = true; break; } }
                    if (match) {
                        if (result.links.length < 20) {
                            result.links.push({
                                tag: allEls[i].tagName, 
                                text: t.substring(0,40), 
                                role: allEls[i].getAttribute('role'),
                                cls: (allEls[i].className||'').substring(0,40)
                            });
                        }
                    }
                }
            }
            
            return result;
        """, self.FB_LANG['publish'], self.FB_LANG['schedule'])
        
        self.logger(f"  🔍 DOM Debug:")
        self.logger(f"  Buttons ({len(dom_debug.get('buttons',[]))}): ")
        for b in dom_debug.get('buttons', [])[:10]:
            self.logger(f"    [{b.get('tag')}] '{b.get('text')}' haspopup={b.get('haspopup')}")
        self.logger(f"  Selects: {dom_debug.get('selects', [])}")
        self.logger(f"  Dropdowns: {dom_debug.get('dropdowns', [])}")
        self.logger(f"  Publish/Schedule elements ({len(dom_debug.get('links',[]))}):")
        for l in dom_debug.get('links', [])[:10]:
            self.logger(f"    [{l.get('tag')}] '{l.get('text')}' role={l.get('role')}")
        
        for idx, video in enumerate(self.video_paths):
            path = video['path']
            video_name = os.path.basename(path)
            video_name_no_ext = os.path.splitext(video_name)[0]
            
            # Nếu là Part 2 (Đăng ngay), Facebook mặc định dòng trạng thái đã là Publish Now. Bỏ qua set lịch!
            if video.get('is_part2'):
                self.logger(f"[{idx+1}/{len(self.video_paths)}] 📹 {video_name_no_ext}")
                self.logger("  ✅ Chế độ Đăng Ngay (Publish Now). Bỏ qua cài đặt Lịch.")
                processed_count += 1
                continue
            
            dt = video['datetime']
            
            # Convert 24h to 12h
            hour_24 = dt.hour
            if hour_24 == 0:
                hour_12, period = 12, "AM"
            elif hour_24 < 12:
                hour_12, period = hour_24, "AM"
            elif hour_24 == 12:
                hour_12, period = 12, "PM"
            else:
                hour_12, period = hour_24 - 12, "PM"
            
            date_str = dt.strftime("%m/%d/%Y")
            target_hour = str(hour_12)
            target_minute = dt.strftime("%M")
            
            self.logger(f"[{idx+1}/{len(self.video_paths)}] 📹 {video_name_no_ext}")
            self.logger(f"  📅 {date_str} {target_hour}:{target_minute} {period}")
            
            try:
                # Đóng popup cũ nếu còn mở
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                    time.sleep(1)
                except: pass
                
                # BƯỚC 1: Tìm Dropdown dựa trên sự gióng hàng tọa độ Y (Visual Y-Alignment)
                # Thay vì tin vào cây DOM (bị React bẻ gãy), ta tìm tọa độ trên màn hình.
                click_result = self.driver.execute_script("""
                    var videoIdx = arguments[0];
                    var pubW = arguments[1]; var schW = arguments[2];
                    
                    // Tìm textarea đại diện cho video (theo index)
                    var allTA = document.querySelectorAll('textarea');
                    var textareas = [];
                    for(var i=0; i<allTA.length; i++) {
                        if ((allTA[i].placeholder||'').length > 5 && allTA[i].getBoundingClientRect().width > 0) {
                            textareas.push(allTA[i]);
                        }
                    }
                    
                    if (textareas.length <= videoIdx) return {success: false, msg: 'Chưa render đủ textarea (tìm thấy ' + textareas.length + ')'};
                    
                    var targetTA = textareas[videoIdx];
                    // Gióng tọa độ Y của textarea này làm tâm
                    targetTA.scrollIntoView({block: 'center'});
                    var taRect = targetTA.getBoundingClientRect();
                    var targetY = taRect.top + taRect.height / 2;
                    
                    // Thu thập tất cả các nút có vẻ liên quan đến Publish/Schedule/Options
                    var btns = document.querySelectorAll('div[role="button"], span[role="button"], button, [tabindex="0"]');
                    var validBtns = [];
                    
                    for(var i=0; i<btns.length; i++) {
                        var rect = btns[i].getBoundingClientRect();
                        if (rect.width === 0 || rect.height === 0) continue;
                        
                        var t = (btns[i].textContent||'').trim().toLowerCase();
                        if (t.length > 2 && t.length < 40) {
                            var isPrimary = false;
                            for(var w=0; w<pubW.length;w++) { if(t.includes(pubW[w])) isPrimary=true; }
                            for(var w=0; w<schW.length;w++) { if(t.includes(schW[w])) isPrimary=true; }
                            
                            var isFallback = t.includes('opsy') || t.includes('option');
                            
                            // Lọc sâu: loại thẻ bọc, chỉ lấy thẻ lõi
                            if((isPrimary || isFallback) && !btns[i].querySelector('div[role="button"], button')) {
                                var btnY = rect.top + rect.height / 2;
                                validBtns.push({btn: btns[i], text: t, isPrimary: isPrimary, dist: Math.abs(btnY - targetY)});
                            }
                        }
                    }
                    
                    if (validBtns.length === 0) return {success: false, msg: 'Không tìm thấy nút nào có text publish/schedule'};
                    
                    // Sắp xếp các nút theo khoảng cách Y so với textarea, ưu tiên Primary nếu cùng hàng
                    validBtns.sort(function(a, b) {
                        if (Math.abs(a.dist - b.dist) < 25) {
                            if (a.isPrimary && !b.isPrimary) return -1;
                            if (!a.isPrimary && b.isPrimary) return 1;
                        }
                        return a.dist - b.dist;
                    });
                    
                    // Nút gần nhất trên cùng trục Y chính là nút của video này
                    var bestBtn = validBtns[0];
                    if (bestBtn.dist > 150) {
                        return {success: false, msg: 'Nút gần nhất lệch trục Y quá xa (' + Math.round(bestBtn.dist) + 'px)'};
                    }
                    
                    bestBtn.btn.click();
                    return {success: true, text: bestBtn.text, dist: bestBtn.dist, method: 'y_alignment'};
                """, idx, self.FB_LANG['publish'], self.FB_LANG['schedule'])
                
                if not click_result or not click_result.get('success'):
                    # Thử lại: scroll down cả body
                    self.driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(1)
                    ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                    click_result = self.driver.execute_script("""
                        var videoIdx = arguments[0];
                        var pubW = arguments[1]; var schW = arguments[2];
                        var allPopups = document.querySelectorAll('[role="button"]');
                        var matched = [];
                        for(var i=0; i<allPopups.length;i++) {
                            var t = (allPopups[i].textContent||'').trim().toLowerCase();
                            var f = false;
                            for (var w=0; w<pubW.length; w++) { if (t.includes(pubW[w])) f=true; }
                            for (var w=0; w<schW.length; w++) { if (t.includes(schW[w])) f=true; }
                            if (f && t.length < 30) matched.push(allPopups[i]);
                        }
                        if (matched.length > videoIdx) {
                            matched[videoIdx].scrollIntoView({block: 'center'});
                            matched[videoIdx].click();
                            return {success: true, text: (matched[videoIdx].textContent||'').trim().substring(0,40), method: 'retry_direct_text'};
                        }
                        return {success: false};
                    """, idx, self.FB_LANG['publish'], self.FB_LANG['schedule'])
                
                if not click_result or not click_result.get('success'):
                    self.logger(f"  ⚠ Không tìm thấy dropdown cho video {idx+1} ({click_result})")
                    continue
                
                self.logger(f"  ✓ Mở dropdown: '{click_result.get('text')}' ({click_result.get('method','?')})")
                time.sleep(0.2)
                
                # BƯỚC 2: Click tab "I-schedule" trong popup
                tab_result = self.driver.execute_script("""
                    var schedWords = arguments[0];
                    var targets = [];
                    // Tìm element LÁ (innermost) chứa schedule text HIỂN THỊ
                    var allEls = document.querySelectorAll('div, span, a');
                    // DUYỆT NGƯỢC: Lấy popup mới nhất sinh ra ở cuối DOM
                    for (var i = allEls.length - 1; i >= 0; i--) {
                        if (allEls[i].getBoundingClientRect().width === 0) continue;
                        
                        var t = (allEls[i].innerText || '').trim();
                        if (t.length > 1 && t.length < 25) {
                            var tl = t.toLowerCase();
                            var match = false;
                            for (var w = 0; w < schedWords.length; w++) {
                                if (tl.includes(schedWords[w])) { match = true; break; }
                            }
                            if (match) {
                                // Kiểm tra lá:
                                var childMatch = false;
                                var children = allEls[i].querySelectorAll('div, span, a');
                                for (var k = 0; k < children.length; k++) {
                                    if (children[k].getBoundingClientRect().width > 0) {
                                        var ctl = (children[k].innerText || '').trim().toLowerCase();
                                        for (var w = 0; w < schedWords.length; w++) {
                                            if (ctl.includes(schedWords[w])) { childMatch = true; break; }
                                        }
                                    }
                                }
                                if (!childMatch) {
                                    allEls[i].click();
                                    return {success: true, text: t, method: 'last_dom_tab'};
                                }
                            }
                        }
                    }
                    return {success: false};
                """, self.FB_LANG['schedule'])
                
                if tab_result and tab_result.get('success'):
                    self.logger(f"  ✓ Tab Schedule: '{tab_result.get('text')}' (leaf={tab_result.get('leaf')})")
                else:
                    self.logger(f"  ⚠ Không thấy tab Schedule")
                
                # Chờ date/time inputs xuất hiện (poll tối đa 5s)
                self.logger("  ⏳ Chờ date/time inputs...")
                for wait_i in range(50):
                    input_check = self.driver.execute_script("""
                        var spins = document.querySelectorAll('input[role="spinbutton"]');
                        var dateInputs = document.querySelectorAll('input[type="text"], input[type="date"]');
                        return {spins: spins.length, inputs: dateInputs.length};
                    """)
                    if input_check and (input_check.get('spins', 0) >= 2 or input_check.get('inputs', 0) >= 3):
                        break
                    time.sleep(0.05)
                else:
                    self.logger(f"  ⚠ Timeout chờ inputs, tiếp tục...")
                
                # DEBUG: Dump inputs
                input_debug = self.driver.execute_script("""
                    var result = {inputs: [], spins: []};
                    var inputs = document.querySelectorAll('input');
                    for (var i = 0; i < inputs.length; i++) {
                        result.inputs.push({
                            type: inputs[i].type,
                            value: (inputs[i].value || '').substring(0, 40),
                            placeholder: (inputs[i].placeholder || '').substring(0, 30),
                            ariaLabel: inputs[i].getAttribute('aria-label'),
                            role: inputs[i].getAttribute('role')
                        });
                    }
                    var spins = document.querySelectorAll('[role="spinbutton"]');
                    for (var i = 0; i < spins.length; i++) {
                        result.spins.push({tag: spins[i].tagName, value: spins[i].value, label: spins[i].getAttribute('aria-label')});
                    }
                    return result;
                """)
                self.logger(f"  📋 Inputs ({len(input_debug.get('inputs',[]))}):")
                for inp in input_debug.get('inputs', []):
                    self.logger(f"    type={inp.get('type')} val='{inp.get('value')}' ph='{inp.get('placeholder')}' label={inp.get('ariaLabel')} role={inp.get('role')}")
                if input_debug.get('spins'):
                    self.logger(f"  Spinbuttons: {input_debug.get('spins')}")
                
                time.sleep(0.1)
                
                # BƯỚC 3: Set ngày bằng Selenium keyboard (React date picker)
                # Tìm date input bằng JS (CHỈ LẤY PHẦN TỬ ĐANG HIỂN THỊ)
                date_idx = self.driver.execute_script("""
                    var monthWords = arguments[0];
                    var dateWords = arguments[1];
                    var allInputs = document.querySelectorAll('input');
                    // DUYỆT NGƯỢC: Lấy popup mới nhất 
                    for (var i = allInputs.length - 1; i >= 0; i--) {
                        // CHẶN NGHIÊM NGẶT CÁC INPUT ẨN
                        var rect = allInputs[i].getBoundingClientRect();
                        if (rect.width === 0 || rect.right < 0 || rect.bottom < 0) continue;
                        
                        var val = (allInputs[i].value || '').toLowerCase();
                        var ph = (allInputs[i].placeholder || '').toLowerCase();
                        var label = (allInputs[i].getAttribute('aria-label') || '').toLowerCase();
                        if (ph.includes('mm/') || ph.includes('dd') || allInputs[i].type === 'date') return i;
                        for (var d = 0; d < dateWords.length; d++) {
                            if (label.includes(dateWords[d]) || ph.includes(dateWords[d])) return i;
                        }
                        if (val.match(/\d{4}/)) return i;
                        var monthFound = false;
                        for (var m = 0; m < monthWords.length; m++) {
                            if (val.includes(monthWords[m])) { monthFound = true; break; }
                        }
                        if (monthFound) return i;
                    }
                    return -1;
                """, self.FB_LANG['months'], self.FB_LANG['date'])
                
                if date_idx is not None and date_idx >= 0:
                    try:
                        all_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input")
                        date_input = all_inputs[date_idx]
                        date_input.click()
                        time.sleep(0.05)
                        date_input.send_keys(Keys.CONTROL + "a")
                        date_input.send_keys(date_str)
                        date_input.send_keys(Keys.RETURN)
                        time.sleep(0.05)
                        self.logger(f"  ✓ Ngày: {date_str}")
                    except Exception as e:
                        self.logger(f"  ❌ Date input error: {e}")
                else:
                    self.logger(f"  ⚠ Không tìm thấy date input")
                
                time.sleep(0.05)
                
                # BƯỚC 4: Set giờ + phút + AM/PM bằng Selenium keyboard (React time picker)
                time_indices = self.driver.execute_script("""
                    var hourWords = arguments[0];
                    var minuteWords = arguments[1];
                    var rawInputs = document.querySelectorAll('input');
                    var allInputs = [];
                    for(var i=0; i<rawInputs.length; i++) {
                        var r = rawInputs[i].getBoundingClientRect();
                        if(r.width > 0 && r.right > 0 && r.bottom > 0) allInputs.push(rawInputs[i]);
                    }
                    
                    var result = {h: -1, m: -1, p: -1, colon: -1, rawIndices: {h:-1, m:-1, p:-1, colon:-1}};
                    
                    // Thử tìm spinbuttons
                    var spins = [];
                    for(var i=0; i<allInputs.length; i++) {
                        if (allInputs[i].getAttribute('role') === 'spinbutton') {
                            for(var r=0; r<rawInputs.length; r++) { if(rawInputs[r]===allInputs[i]) spins.push(r); }
                        }
                    }
                    // LUÔN LẤY SPINS Ở CUỐI MẢNG TỨC LÀ Ở POPUP MỚI NHẤT
                    if (spins.length >= 2) {
                        var L = spins.length;
                        if (L >= 3) {
                            result.rawIndices.h = spins[L-3];
                            result.rawIndices.m = spins[L-2];
                            result.rawIndices.p = spins[L-1];
                        } else {
                            result.rawIndices.h = spins[L-2];
                            result.rawIndices.m = spins[L-1];
                        }
                        return result.rawIndices;
                    }
                    
                    // Nếu không có spinbutton, quét ngược
                    for (var i = allInputs.length - 1; i >= 0; i--) {
                        var label = (allInputs[i].getAttribute('aria-label') || '').toLowerCase();
                        var val = (allInputs[i].value || '').trim();
                        
                        var rIndex = -1;
                        for(var r=0; r<rawInputs.length; r++) { if(rawInputs[r]===allInputs[i]) { rIndex=r; break;} }
                        
                        if (val.match(/^\\d{1,2}:\\d{2}$/)) result.rawIndices.colon = rIndex;
                        
                        var isHour = false, isMin = false;
                        for (var w = 0; w < hourWords.length; w++) { if (label.includes(hourWords[w])) { isHour = true; break; } }
                        if (!isHour) for (var w = 0; w < minuteWords.length; w++) { if (label.includes(minuteWords[w])) { isMin = true; break; } }
                        
                        if (isHour) result.rawIndices.h = rIndex;
                        if (isMin) result.rawIndices.m = rIndex;
                        if (label.includes('meridiem') || label === 'am/pm') result.rawIndices.p = rIndex;
                    }
                    return result.rawIndices;
                """, self.FB_LANG['hours'], self.FB_LANG['minutes'])
                
                all_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input")
                time_set_success = False
                
                try:
                    if time_indices:
                        if time_indices.get('colon', -1) >= 0 and time_indices['colon'] < len(all_inputs):
                            # Trường hợp facebook hiển thị 1 ô input duy nhất HH:MM
                            colon_input = all_inputs[time_indices['colon']]
                            colon_input.click()
                            time.sleep(0.05)
                            colon_input.send_keys(Keys.CONTROL + "a")
                            colon_input.send_keys(f"{target_hour.zfill(2)}:{target_minute}")
                            time_set_success = True
                        elif time_indices.get('h', -1) >= 0 and time_indices['h'] < len(all_inputs):
                            # Trường hợp tách rời spinbuttons
                            h_in = all_inputs[time_indices['h']]
                            m_in = all_inputs[time_indices['m']]
                            p_in = all_inputs[time_indices['p']] if time_indices.get('p', -1) >= 0 else None
                            
                            # Set Hour
                            h_in.click()
                            time.sleep(0.05)
                            h_in.send_keys(Keys.CONTROL + "a")
                            h_in.send_keys(target_hour)
                            
                            # Set Minute
                            m_in.click()
                            time.sleep(0.05)
                            m_in.send_keys(Keys.CONTROL + "a")
                            m_in.send_keys(target_minute)
                            
                            # Set AM/PM
                            if p_in:
                                p_in.click()
                                time.sleep(0.05)
                                p_in.send_keys(period.lower()[0]) # 'a' hoặc 'p'
                            
                            time_set_success = True
                            
                    if time_set_success:
                        self.logger(f"  ✓ Time: {target_hour}:{target_minute} {period}")
                    else:
                        self.logger(f"  ⚠ Không tìm thấy Time input")
                except Exception as e:
                    self.logger(f"  ❌ Lỗi nhập Time: {e}")
                
                time.sleep(0.1)
                
                # BƯỚC 5: Click "I-update" (CHỈ update, KHÔNG save/draft)
                update_clicked = False
                for attempt in range(3):
                    update_result = self.driver.execute_script("""
                        var updateWords = arguments[0];
                        
                        // CỐ LẬP TÌM KIẾM TRONG POPUP ACTIVE (để tránh click nhầm nút Publish chung của toàn trang)
                        var dialogs = document.querySelectorAll('div[role="dialog"], div[class*="modal"], div[class*="popup"]');
                        var activeDialog = null;
                        for (var d = dialogs.length - 1; d >= 0; d--) {
                            if (dialogs[d].getBoundingClientRect().width > 0) {
                                activeDialog = dialogs[d];
                                break;
                            }
                        }
                        
                        var container = activeDialog ? activeDialog : document;
                        var buttons = container.querySelectorAll('[role="button"], button');
                        
                        // Bước 1: Tìm nút "update" (DUYỆT NGƯỢC)
                        for (var i = buttons.length - 1; i >= 0; i--) {
                            var r = buttons[i].getBoundingClientRect();
                            if (r.width === 0 || r.right < 0 || r.bottom < 0) continue;
                            
                            var text = (buttons[i].textContent || '').trim().toLowerCase();
                            if (text.length > 1 && text.length < 25) {
                                if (text.includes('draft') || text.includes('bilang') || text.includes('nháp') || text.includes('publish') || text.includes('cancel')) continue;
                                var found = false;
                                for (var w = 0; w < updateWords.length; w++) {
                                    if (text.includes(updateWords[w])) { found = true; break; }
                                }
                                if (found) {
                                    buttons[i].click();
                                    return {success: true, text: (buttons[i].textContent||'').trim(), method: 'update_text'};
                                }
                            }
                        }
                        // Bước 2: Fallback nút xanh (DUYỆT NGƯỢC TRONG POPUP)
                        for (var i = buttons.length - 1; i >= 0; i--) {
                            var r = buttons[i].getBoundingClientRect();
                            if (r.width === 0 || r.right < 0 || r.bottom < 0) continue;
                            
                            var text = (buttons[i].textContent || '').trim().toLowerCase();
                            if (text.length > 1 && text.length < 25) {
                                if (text.includes('draft') || text.includes('bilang') || text.includes('nháp') || text.includes('publish') || text.includes('cancel')) continue;
                                // Kiểm tra màu nền (ví dụ: màu xanh của nút chính)
                                var style = window.getComputedStyle(buttons[i]);
                                var bgColor = style.backgroundColor;
                                // Một số màu xanh phổ biến của nút chính trên Facebook
                                if (bgColor.includes('rgb(45, 136, 255)') || bgColor.includes('rgb(24, 119, 242)')) {
                                    buttons[i].click();
                                    return {success: true, text: (buttons[i].textContent||'').trim(), method: 'update_color_fallback'};
                                }
                            }
                        }
                        return {success: false};
                    """, self.FB_LANG['update'])
                    
                    if update_result and update_result.get('success'):
                        self.logger(f"  ✓ Click '{update_result.get('text')}'")
                        update_clicked = True
                        break
                    time.sleep(0.2)

                if not update_clicked:
                    self.logger("  ⚠ Không thấy nút Update")

                # ĐÓNG POPUP - Chờ và đảm bảo popup đóng hoàn toàn tự nhiên sau khi click Update
                for wait_attempt in range(20):
                    popup_exists = self.driver.execute_script("""
                        var allDivs = document.querySelectorAll('div[role="dialog"], div[class*="modal"], div[class*="popup"]');
                        for (var i = 0; i < allDivs.length; i++) {
                            if (allDivs[i].getBoundingClientRect().width > 0) {
                                var text = allDivs[i].textContent.toLowerCase();
                                if (text.includes('schedule') || text.includes('publish') || text.includes('update')) {
                                    return true;
                                }
                            }
                        }
                        return false;
                    """)
                    
                    if not popup_exists:
                        break
                    time.sleep(0.1)
                
                # Nếu popup vẫn ngoan cố chưa đóng hoặc bị lỗi (update_clicked = False), ép đóng bằng phím ESC
                if popup_exists or not update_clicked:
                    try:
                        from selenium.webdriver.common.action_chains import ActionChains
                        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                        time.sleep(0.2)
                    except:
                        pass

                self.logger("  🔒 Popup đã đóng")
                processed_count += 1
                
            except Exception as e:
                self.logger(f"  ❌ Lỗi xử lý video: {e}")
                
        return processed_count

    def _fill_description_with_js(self, text, row_index):
        """
        Điền Mô tả bằng JavaScript - CHỜ textarea xuất hiện rồi mới điền
        """
        self.logger(f"🚀 Tìm textarea Mô tả...")
        
        try:
            # Bước 1: CHỜ textarea Mô tả xuất hiện (timeout 10s)
            self.logger("  ⏳ Chờ textarea Mô tả render...")
            max_wait = 10
            start = time.time()
            textarea_found = False
            
            while not textarea_found and (time.time() - start) < max_wait:
                textarea_found = self.driver.execute_script("""
                    const textareas = document.querySelectorAll('textarea');
                    for (let ta of textareas) {
                        const placeholder = (ta.placeholder || '').toLowerCase();
                        if (placeholder.includes('mô tả')) {
                            return true;
                        }
                    }
                    return false;
                """)
                if not textarea_found:
                    time.sleep(0.5)
            
            if not textarea_found:
                self.logger("  ❌ Timeout - textarea Mô tả chưa xuất hiện!")
                return False
            
            self.logger("  ✓ Textarea Mô tả đã xuất hiện!")
            time.sleep(0.5)
            
            # Bước 2: Điền nội dung
            fill_success = self.driver.execute_script("""
                const text = arguments[0];
                
                // Tìm textarea có placeholder "Mô tả"
                const textareas = Array.from(document.querySelectorAll('textarea'));
                let targetTextarea = null;
                
                for (let ta of textareas) {
                    const placeholder = (ta.placeholder || '').toLowerCase();
                    const ariaLabel = (ta.getAttribute('aria-label') || '').toLowerCase();
                    
                    if (placeholder.includes('mô tả') || ariaLabel.includes('mô tả')) {
                        targetTextarea = ta;
                        break;
                    }
                }
                
                // Nếu không tìm thấy theo placeholder, lấy textarea cuối (thường là Mô tả)
                if (!targetTextarea && textareas.length > 0) {
                    targetTextarea = textareas[textareas.length - 1];
                }
                
                if (!targetTextarea) return false;
                
                // Scroll vào view
                targetTextarea.scrollIntoView({block: 'center', behavior: 'smooth'});
                
                // Điền nội dung
                targetTextarea.value = text;
                targetTextarea.focus();
                
                // Trigger events
                targetTextarea.dispatchEvent(new Event('input', { bubbles: true }));
                targetTextarea.dispatchEvent(new Event('change', { bubbles: true }));
                targetTextarea.dispatchEvent(new Event('blur', { bubbles: true }));
                
                return true;
            """, text)
            
            if fill_success:
                self.logger(f"  ✓ Điền Mô tả thành công: '{text}'")
                time.sleep(0.5)
                
                # Verify
                value = self.driver.execute_script("""
                    const textareas = document.querySelectorAll('textarea');
                    for (let ta of textareas) {
                        const placeholder = (ta.placeholder || '').toLowerCase();
                        if (placeholder.includes('mô tả')) {
                            return ta.value;
                        }
                    }
                    return textareas.length > 0 ? textareas[textareas.length - 1].value : '';
                """)
                
                if text in value:
                    self.logger(f"  ✓ Verified: '{value}'")
                    return True
                else:
                    self.logger(f"  ⚠ Verify failed: '{value}'")
                    return False
            else:
                self.logger("  ⚠ Không tìm thấy textarea Mô tả")
                return False
                
        except Exception as e:
            self.logger(f"  ❌ Lỗi: {e}")
            return False
    
    def _fill_description(self, text, row_index):
        """
        Điền Mô tả bằng cách click vào cột Mô tả để mở editor
        Args:
            text: Nội dung cần điền
            row_index: Index của row mới (0-indexed)
        Returns: True nếu thành công, False nếu thất bại
        """
        self.logger(f"🔍 Đang tìm cột Mô tả cho row index {row_index}...")
        
        try:
            # Bước 1: Tìm và click vào cột "Mô tả" để mở editor
            desc_trigger = None
            
            # Chiến lược 1: Tìm div có placeholder chứa "Mô tả"
            try:
                desc_triggers = self.driver.find_elements(By.XPATH, 
                    "//div[contains(@role, 'textbox') or contains(@contenteditable, 'true')]//div[contains(text(), 'Mô tả') or contains(@placeholder, 'Mô tả')]")
                if desc_triggers:
                    desc_trigger = desc_triggers[-1]  # Lấy cái cuối (row mới nhất)
                    self.logger(f"  ✓ Tìm thấy cột Mô tả (chiến lược #1)")
            except:
                pass
            
            # Chiến lược 2: Tìm div trong cột "Mô tả" (theo header)
            if not desc_trigger:
                try:
                    # Tìm tất cả các div có thể click trong cột Mô tả
                    desc_triggers = self.driver.find_elements(By.XPATH, 
                        "//div[contains(text(), 'Mô tả')]//ancestor::div[contains(@role, 'columnheader')]//following-sibling::div//div[@role='textbox' or @contenteditable='true']")
                    if desc_triggers:
                        desc_trigger = desc_triggers[-1]
                        self.logger(f"  ✓ Tìm thấy cột Mô tả (chiến lược #2)")
                except:
                    pass
            
            # Chiến lược 3: Tìm theo text placeholder
            if not desc_trigger:
                try:
                    desc_triggers = self.driver.find_elements(By.XPATH, 
                        "//*[contains(text(), 'thuộc phim') or contains(text(), 'Mô tả')]")
                    if desc_triggers:
                        desc_trigger = desc_triggers[-1]
                        self.logger(f"  ✓ Tìm thấy cột Mô tả (chiến lược #3)")
                except:
                    pass
            
            if not desc_trigger:
                self.logger("❌ Không tìm thấy cột Mô tả để click!")
                return False
            
            # Scroll vào view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", desc_trigger)
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
            
            # Bước 2: Tìm textarea trong popup/editor đã mở
            desc_textarea = None
            
            # Tìm textarea mới xuất hiện (thường là textarea cuối cùng)
            try:
                all_textareas = self.driver.find_elements(By.XPATH, "//textarea")
                if all_textareas:
                    # Lấy textarea cuối cùng (vừa mở)
                    desc_textarea = all_textareas[-1]
                    placeholder = desc_textarea.get_attribute("placeholder") or "N/A"
                    self.logger(f"  ✓ Tìm thấy textarea trong editor (placeholder: '{placeholder}')")
            except:
                pass
            
            # Fallback: Tìm div contenteditable
            if not desc_textarea:
                try:
                    contenteditable_divs = self.driver.find_elements(By.XPATH, 
                        "//div[@contenteditable='true' and not(contains(@aria-label, 'Tiêu đề'))]")
                    if contenteditable_divs:
                        desc_textarea = contenteditable_divs[-1]
                        self.logger(f"  ✓ Tìm thấy div contenteditable trong editor")
                except:
                    pass
            
            if not desc_textarea:
                self.logger("❌ Không tìm thấy textarea/editor sau khi click!")
                # Remove highlight
                self.driver.execute_script("""
                    arguments[0].style.border = '';
                    arguments[0].style.backgroundColor = '';
                """, desc_trigger)
                return False
            
            # Bước 3: Điền nội dung
            success = self._try_fill_textarea(desc_textarea, text)
            
            # Remove highlight
            self.driver.execute_script("""
                arguments[0].style.border = '';
                arguments[0].style.backgroundColor = '';
            """, desc_trigger)
            
            return success
            
        except Exception as e:
            self.logger(f"❌ Lỗi điền Mô tả: {e}")
            import traceback
            self.logger(f"Traceback: {traceback.format_exc()}")
            return False
    
    def _find_textarea_by_index(self, index):
        """Tìm textarea theo index chính xác"""
        try:
            all_textareas = self.driver.find_elements(By.XPATH, "//textarea")
            if 0 <= index < len(all_textareas):
                self.logger(f"  ✓ Tìm thấy textarea tại index {index}/{len(all_textareas)}")
                return all_textareas[index]
            else:
                self.logger(f"  ✗ Index {index} ngoài phạm vi (có {len(all_textareas)} textarea)")
        except Exception as e:
            self.logger(f"  ✗ Lỗi tìm theo index: {e}")
        return None
    
    def _find_textarea_by_placeholder(self):
        """Tìm textarea theo placeholder"""
        try:
            return self.driver.find_element(By.XPATH, 
                "//textarea[contains(@placeholder, 'Mô tả') or contains(@placeholder, 'mô tả') or contains(@placeholder, 'Description')]")
        except:
            return None
    
    def _find_textarea_in_video_row(self):
        """Tìm textarea trong row có video vừa upload (row mới nhất)"""
        try:
            # Cách 1: Tìm row có "100%" gần nhất (vừa upload xong)
            # Lấy TẤT CẢ các row có 100%, rồi lấy cái cuối cùng
            rows_with_100 = self.driver.find_elements(By.XPATH, 
                "//div[contains(., '100%')]/ancestor::div[contains(@role, 'row') or contains(@class, 'row') or contains(@data-testid, 'row')]")
            
            if rows_with_100:
                # Lấy row cuối cùng (mới nhất)
                latest_row = rows_with_100[-1]
                self.logger(f"  Tìm thấy {len(rows_with_100)} row có 100%, dùng row cuối")
                
                # Tìm textarea trong row đó
                textareas_in_row = latest_row.find_elements(By.XPATH, ".//textarea")
                if textareas_in_row:
                    self.logger(f"  Tìm thấy {len(textareas_in_row)} textarea trong row mới nhất")
                    return textareas_in_row[-1]  # Lấy textarea cuối trong row
            
            # Cách 2: Tìm theo index - đếm số video đã upload
            # Giả sử mỗi row có 1 textarea, row thứ N có textarea thứ N
            all_textareas = self.driver.find_elements(By.XPATH, "//textarea")
            all_rows = self.driver.find_elements(By.XPATH, 
                "//div[contains(@role, 'row') or contains(@class, 'row')]")
            
            if all_textareas and all_rows:
                # Lấy textarea cuối cùng (tương ứng row cuối)
                self.logger(f"  Tìm thấy {len(all_textareas)} textarea, {len(all_rows)} rows")
                return all_textareas[-1]
            
        except Exception as e:
            self.logger(f"  Lỗi tìm textarea trong row: {e}")
        
        return None
    
    def _find_last_textarea(self):
        """Tìm textarea cuối cùng trên trang"""
        try:
            textareas = self.driver.find_elements(By.XPATH, "//textarea")
            if textareas:
                self.logger(f"  Tìm thấy {len(textareas)} textarea, dùng cái cuối")
                return textareas[-1]
        except:
            pass
        return None
    
    def _try_fill_textarea(self, element, text):
        """Thử điền text vào textarea với nhiều phương pháp"""
        
        # Scroll vào view
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
            time.sleep(1)
        except:
            pass
        
        # Phương pháp 1: send_keys thông thường
        try:
            self.driver.execute_script("arguments[0].focus();", element)
            time.sleep(0.3)
            element.click()
            time.sleep(0.5)
            
            # Clear
            self.driver.execute_script("arguments[0].value = '';", element)
            element.clear()
            element.send_keys(Keys.CONTROL + "a")
            element.send_keys(Keys.BACKSPACE)
            time.sleep(0.3)
            
            # Điền
            element.send_keys(text)
            time.sleep(1)
            
            # Trigger events
            self.driver.execute_script("""
                var el = arguments[0];
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('blur', { bubbles: true }));
            """, element)
            time.sleep(0.5)
            
            # Verify
            value = self.driver.execute_script("return arguments[0].value;", element)
            if value and text in value:
                self.logger(f"✓ Điền thành công: '{value}'")
                return True
            else:
                self.logger(f"⚠ Phương pháp 1 thất bại. Got: '{value}'")
        except Exception as e:
            self.logger(f"⚠ Phương pháp 1 lỗi: {e}")
        
        # Phương pháp 2: Dùng clipboard (paste)
        try:
            import pyperclip
            pyperclip.copy(text)
            
            element.click()
            time.sleep(0.3)
            element.send_keys(Keys.CONTROL + "a")
            element.send_keys(Keys.CONTROL + "v")
            time.sleep(1)
            
            value = self.driver.execute_script("return arguments[0].value;", element)
            if value and text in value:
                self.logger(f"✓ Điền thành công bằng paste: '{value}'")
                return True
            else:
                self.logger(f"⚠ Phương pháp 2 thất bại. Got: '{value}'")
        except Exception as e:
            self.logger(f"⚠ Phương pháp 2 lỗi: {e}")
        
        # Phương pháp 3: Dùng JS trực tiếp
        try:
            self.driver.execute_script("arguments[0].value = arguments[1];", element, text)
            self.driver.execute_script("""
                var el = arguments[0];
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            """, element)
            time.sleep(1)
            
            value = self.driver.execute_script("return arguments[0].value;", element)
            if value and text in value:
                self.logger(f"✓ Điền thành công bằng JS: '{value}'")
                return True
            else:
                self.logger(f"⚠ Phương pháp 3 thất bại. Got: '{value}'")
        except Exception as e:
            self.logger(f"⚠ Phương pháp 3 lỗi: {e}")
        
        self.logger("❌ Tất cả phương pháp đều thất bại!")
        return False
