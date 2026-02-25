import json
import os
import string
import random
from datetime import datetime, timedelta
from services.adminservices.key_service import KeyService


class AdminController:
    """Controller cho Admin Key Manager"""
    
    def __init__(self, admin_window):
        self.window = admin_window
        self.config_path = "temp/admin_config.json"
        self.key_service = None
        self.keys_data = {"keys": []}
        
        # Bind callbacks
        self.window.on_connect = self.connect_github
        self.window.on_add_key = self.add_key
        self.window.on_delete_key = self.delete_key
        self.window.on_toggle_key = self.toggle_key
        self.window.on_edit_key = self.edit_key
        self.window.on_refresh = self.refresh_keys
        
        # Auto-load saved token
        self._load_saved_token()
    
    def _load_saved_token(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                token = config.get("github_token", "")
                if token:
                    self.window.set_token(token)
        except:
            pass
    
    def _save_token(self, token):
        os.makedirs("temp", exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump({"github_token": token}, f)
    
    def connect_github(self, token):
        if not token.strip():
            self.window.log("⚠ Vui lòng nhập GitHub Token!")
            return
        
        self.key_service = KeyService(github_token=token.strip())
        self._save_token(token.strip())
        self.window.log("🔗 Đang kết nối GitHub...")
        self.refresh_keys()
    
    def refresh_keys(self):
        if not self.key_service:
            self.window.log("⚠ Chưa kết nối GitHub! Nhập token và nhấn Kết nối.")
            return
        
        keys_data = self.key_service.fetch_keys()
        if keys_data is not None:
            self.keys_data = keys_data
            keys = keys_data.get("keys", [])
            self.window.display_keys(keys)
            self.window.log(f"✅ Đã tải {len(keys)} license keys từ GitHub")
        else:
            self.window.log("❌ Không thể kết nối GitHub. Kiểm tra token!")
    
    @staticmethod
    def generate_key():
        chars = string.ascii_uppercase + string.digits
        parts = [''.join(random.choices(chars, k=4)) for _ in range(4)]
        return '-'.join(parts)
    
    def add_key(self, note, days):
        if not self.key_service:
            self.window.log("⚠ Chưa kết nối GitHub!")
            return
        
        try:
            days = int(days)
        except:
            days = 30
        
        new_key = {
            "key": self.generate_key(),
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "expires_at": (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d"),
            "status": "active",
            "note": note or "No note"
        }
        
        self.keys_data.setdefault("keys", []).append(new_key)
        
        self.window.log("⏳ Đang lưu key mới lên GitHub...")
        success, msg = self.key_service.save_keys(self.keys_data)
        
        if success:
            self.window.display_keys(self.keys_data["keys"])
            self.window.log(f"✅ Đã tạo key: {new_key['key']} ({days} ngày)")
        else:
            self.keys_data["keys"].pop()
            self.window.log(f"❌ Lỗi tạo key: {msg}")
    
    def delete_key(self, key_value):
        if not self.key_service:
            return
        
        self.keys_data["keys"] = [
            k for k in self.keys_data.get("keys", []) if k["key"] != key_value
        ]
        
        self.window.log(f"⏳ Đang xoá key...")
        success, msg = self.key_service.save_keys(self.keys_data)
        if success:
            self.window.display_keys(self.keys_data["keys"])
            self.window.log(f"🗑️ Đã xoá key: {key_value}")
        else:
            self.window.log(f"❌ Lỗi xoá key: {msg}")
            self.refresh_keys()
    
    def toggle_key(self, key_value):
        if not self.key_service:
            return
        
        old_status = ""
        for k in self.keys_data.get("keys", []):
            if k["key"] == key_value:
                old_status = k["status"]
                k["status"] = "disabled" if old_status == "active" else "active"
                break
        
        self.window.log(f"⏳ Đang cập nhật trạng thái...")
        success, msg = self.key_service.save_keys(self.keys_data)
        if success:
            new_status = "disabled" if old_status == "active" else "active"
            self.window.display_keys(self.keys_data["keys"])
            self.window.log(f"🔄 Key {key_value}: {old_status} → {new_status}")
        else:
            self.window.log(f"❌ Lỗi: {msg}")
            self.refresh_keys()
    
    def edit_key(self, key_value, new_note, new_days):
        if not self.key_service:
            return
        
        for k in self.keys_data.get("keys", []):
            if k["key"] == key_value:
                if new_note:
                    k["note"] = new_note
                if new_days:
                    try:
                        k["expires_at"] = (datetime.now() + timedelta(days=int(new_days))).strftime("%Y-%m-%d")
                    except:
                        pass
                break
        
        self.window.log(f"⏳ Đang cập nhật key...")
        success, msg = self.key_service.save_keys(self.keys_data)
        if success:
            self.window.display_keys(self.keys_data["keys"])
            self.window.log(f"✏️ Đã sửa key: {key_value}")
        else:
            self.window.log(f"❌ Lỗi: {msg}")
            self.refresh_keys()
