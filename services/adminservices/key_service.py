import requests
import json
import base64
from datetime import datetime


class KeyService:
    """Service quản lý license keys qua GitHub API"""
    
    REPO = "nguyenduyducds/tooldatlich"
    FILE_PATH = "keys/license_keys.json"
    
    def __init__(self, github_token=None):
        self.github_token = github_token
        self.api_url = f"https://api.github.com/repos/{self.REPO}/contents/{self.FILE_PATH}"
        self.sha = None
    
    def _headers(self):
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "FBScheduler-Admin"
        }
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        return headers
    
    def fetch_keys(self):
        """Lấy danh sách keys từ GitHub"""
        try:
            resp = requests.get(self.api_url, headers=self._headers(), timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                self.sha = data.get("sha")
                content = base64.b64decode(data["content"]).decode("utf-8")
                return json.loads(content)
            elif resp.status_code == 404:
                # File chưa tồn tại → trả về rỗng
                return {"keys": []}
            else:
                print(f"GitHub API Error: {resp.status_code} - {resp.text}")
                return None
        except Exception as e:
            print(f"Fetch keys error: {e}")
            return None
    
    def save_keys(self, keys_data):
        """Lưu keys lên GitHub"""
        if not self.github_token:
            return False, "Cần GitHub Token để lưu!"
        
        try:
            content = json.dumps(keys_data, indent=2, ensure_ascii=False)
            encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
            
            payload = {
                "message": f"Update license keys - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "content": encoded,
                "branch": "main"
            }
            if self.sha:
                payload["sha"] = self.sha
            
            resp = requests.put(self.api_url, headers=self._headers(), json=payload, timeout=15)
            
            if resp.status_code in (200, 201):
                result = resp.json()
                self.sha = result.get("content", {}).get("sha")
                return True, "Đã lưu thành công!"
            else:
                msg = resp.json().get("message", "Unknown error")
                return False, f"GitHub Error: {resp.status_code} - {msg}"
        except Exception as e:
            return False, f"Lỗi kết nối: {e}"
    
    def validate_key(self, key_str):
        """Kiểm tra key có hợp lệ không (dùng cho login, không cần token)"""
        keys_data = self.fetch_keys()
        if keys_data is None:
            return False, "Không thể kết nối server để xác thực"
        
        for k in keys_data.get("keys", []):
            if k.get("key") == key_str:
                if k.get("status") != "active":
                    return False, "Key đã bị vô hiệu hoá"
                
                # Check hết hạn
                expires = k.get("expires_at", "")
                if expires:
                    try:
                        exp_date = datetime.strptime(expires, "%Y-%m-%d")
                        if datetime.now() > exp_date:
                            return False, f"Key đã hết hạn ({expires})"
                    except:
                        pass
                
                return True, f"Đăng nhập thành công! (Hết hạn: {expires})"
        
        return False, "Key không tồn tại"
