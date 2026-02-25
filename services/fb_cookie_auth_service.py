import requests
import os
import time
import json
from datetime import datetime

class FacebookCookieAuthService:
    """
    Service để đăng video lên Facebook bằng cách dùng cookies từ browser
    Không cần Access Token chính thức, bypass bằng cách lấy token từ session
    """
    
    def __init__(self, cookies_dict, page_id, video_paths, logger):
        """
        Args:
            cookies_dict: Dict cookies từ browser {"c_user": "...", "xs": "...", ...}
            page_id: ID của Page
            video_paths: List video data
            logger: Function để log
        """
        self.cookies = cookies_dict
        self.page_id = page_id
        self.video_paths = video_paths
        self.logger = logger
        self.base_url = "https://graph.facebook.com/v18.0"
        self.access_token = None
    
    def extract_token_from_cookies(self):
        """
        Lấy access token từ cookies bằng cách gọi API với cookies
        """
        try:
            # Thử lấy token từ /me endpoint
            url = "https://www.facebook.com/me"
            response = requests.get(url, cookies=self.cookies, allow_redirects=True)
            
            # Parse HTML để tìm access token (thường có trong script tags)
            # Hoặc dùng cách khác: gọi internal API
            
            # Cách 2: Dùng internal API endpoint
            internal_url = "https://www.facebook.com/api/graphql/"
            
            # Lấy dtsg token (cần cho POST requests)
            dtsg = self._extract_dtsg()
            
            if dtsg:
                self.logger("✓ Đã lấy được DTSG token từ cookies")
                return True
            else:
                self.logger("❌ Không lấy được DTSG token")
                return False
                
        except Exception as e:
            self.logger(f"❌ Lỗi extract token: {e}")
            return False
    
    def _extract_dtsg(self):
        """Extract fb_dtsg token từ Facebook page"""
        try:
            url = "https://www.facebook.com/"
            response = requests.get(url, cookies=self.cookies)
            
            # Tìm fb_dtsg trong HTML
            import re
            match = re.search(r'"DTSGInitialData",\[\],{"token":"([^"]+)"', response.text)
            if match:
                return match.group(1)
            
            # Fallback: tìm pattern khác
            match = re.search(r'{"dtsg":{"token":"([^"]+)"', response.text)
            if match:
                return match.group(1)
                
            return None
        except:
            return None
    
    def run_task(self):
        """Upload videos bằng cookies"""
        self.logger("🚀 Bắt đầu upload video qua Facebook Cookies...")
        
        # Verify cookies
        if not self.verify_cookies():
            self.logger("❌ Cookies không hợp lệ hoặc đã hết hạn!")
            return
        
        if not self.video_paths:
            self.logger("❌ Không có video nào để upload!")
            return
        
        success_count = 0
        
        for video_data in self.video_paths:
            path = video_data['path']
            dt = video_data['datetime']
            
            video_name = os.path.basename(path)
            video_name_no_ext = os.path.splitext(video_name)[0]
            
            self.logger(f"📹 Đang xử lý: {video_name}")
            
            try:
                description = video_name_no_ext
                scheduled_time = int(dt.timestamp())
                
                # Upload qua internal API (không cần official token)
                video_id = self.upload_video_with_cookies(
                    video_path=path,
                    title=video_name_no_ext,
                    description=description,
                    scheduled_time=scheduled_time
                )
                
                if video_id:
                    self.logger(f"✓ Upload thành công! Video ID: {video_id}")
                    success_count += 1
                else:
                    self.logger(f"❌ Upload thất bại: {video_name}")
                
                time.sleep(2)
                
            except Exception as e:
                self.logger(f"❌ Lỗi xử lý {video_name}: {e}")
        
        self.logger(f"✓ Hoàn thành! {success_count}/{len(self.video_paths)} video đã upload.")
    
    def verify_cookies(self):
        """Kiểm tra cookies có hợp lệ không"""
        try:
            url = "https://www.facebook.com/me"
            response = requests.get(url, cookies=self.cookies, allow_redirects=False)
            
            # Nếu redirect về login -> cookies hết hạn
            if response.status_code == 302 and 'login' in response.headers.get('Location', ''):
                return False
            
            # Nếu có c_user trong cookies và response OK
            if 'c_user' in self.cookies and response.status_code == 200:
                self.logger("✓ Cookies hợp lệ!")
                return True
            
            return False
            
        except Exception as e:
            self.logger(f"❌ Lỗi verify cookies: {e}")
            return False
    
    def upload_video_with_cookies(self, video_path, title, description, scheduled_time):
        """
        Upload video bằng internal Facebook API (không cần official token)
        Sử dụng cookies để authenticate
        """
        try:
            # Facebook internal upload endpoint
            # Cần reverse engineer từ Network tab khi upload thủ công
            
            # Lấy upload session
            dtsg = self._extract_dtsg()
            if not dtsg:
                self.logger("  ❌ Không lấy được DTSG token")
                return None
            
            # Bước 1: Khởi tạo upload session
            init_url = f"https://upload.facebook.com/ajax/mercury/upload.php"
            
            # Bước 2: Upload file chunks
            # (Code phức tạp, cần reverse engineer chi tiết)
            
            # Bước 3: Finalize và schedule
            
            self.logger("  ⚠ Upload qua cookies cần reverse engineer thêm...")
            self.logger("  💡 Khuyến nghị: Dùng Selenium hoặc đăng ký Developer để lấy token chính thức")
            
            return None
            
        except Exception as e:
            self.logger(f"  ❌ Exception: {e}")
            return None
