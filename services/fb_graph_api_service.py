import requests
import os
import time
from datetime import datetime

class FacebookGraphAPIService:
    """
    Service để đăng video lên Facebook Page bằng Graph API
    Docs: https://developers.facebook.com/docs/graph-api/reference/page/videos
    """
    
    def __init__(self, page_id, access_token, video_paths, logger):
        self.page_id = page_id
        self.access_token = access_token
        self.video_paths = video_paths  # [{"path": ..., "datetime": ..., "format": ...}]
        self.logger = logger
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def run_task(self):
        """Upload và schedule videos"""
        self.logger("🚀 Bắt đầu upload video qua Facebook Graph API...")
        
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
                # Tạo description từ tên file
                description = video_name_no_ext
                
                # Tính scheduled_publish_time (Unix timestamp)
                scheduled_time = int(dt.timestamp())
                
                # Upload video
                video_id = self.upload_video(
                    video_path=path,
                    title=video_name_no_ext,
                    description=description,
                    scheduled_time=scheduled_time
                )
                
                if video_id:
                    self.logger(f"✓ Upload thành công! Video ID: {video_id}")
                    self.logger(f"  - Tiêu đề: {video_name_no_ext}")
                    self.logger(f"  - Mô tả: {description}")
                    self.logger(f"  - Lịch đăng: {dt.strftime('%d/%m/%Y %H:%M')}")
                    success_count += 1
                else:
                    self.logger(f"❌ Upload thất bại: {video_name}")
                
                time.sleep(2)  # Chờ giữa các video
                
            except Exception as e:
                self.logger(f"❌ Lỗi xử lý {video_name}: {e}")
        
        self.logger(f"✓ Hoàn thành! {success_count}/{len(self.video_paths)} video đã upload.")
    
    def upload_video(self, video_path, title, description, scheduled_time):
        """
        Upload video lên Facebook Page với schedule
        
        Returns:
            str: Video ID nếu thành công, None nếu thất bại
        """
        try:
            # Endpoint
            url = f"{self.base_url}/{self.page_id}/videos"
            
            # Parameters
            params = {
                'access_token': self.access_token,
                'title': title,
                'description': description,
                'published': 'false',  # Không đăng ngay
                'scheduled_publish_time': scheduled_time,  # Unix timestamp
            }
            
            # File
            with open(video_path, 'rb') as video_file:
                files = {
                    'source': video_file
                }
                
                self.logger(f"  Đang upload... (có thể mất vài phút)")
                
                # POST request
                response = requests.post(url, data=params, files=files, timeout=600)
                
                # Check response
                if response.status_code == 200:
                    result = response.json()
                    return result.get('id')
                else:
                    error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                    self.logger(f"  API Error: {error_msg}")
                    return None
                    
        except Exception as e:
            self.logger(f"  Exception: {e}")
            return None
    
    def test_connection(self):
        """Test xem access token có hợp lệ không"""
        try:
            url = f"{self.base_url}/{self.page_id}"
            params = {
                'access_token': self.access_token,
                'fields': 'id,name'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.logger(f"✓ Kết nối thành công! Page: {data.get('name')}")
                return True
            else:
                error = response.json().get('error', {})
                self.logger(f"❌ Lỗi kết nối: {error.get('message')}")
                return False
                
        except Exception as e:
            self.logger(f"❌ Exception: {e}")
            return False
