import customtkinter as ctk
import threading
import os
import json


class LoginWindow(ctk.CTk):
    """Màn hình đăng nhập bằng License Key"""
    
    def __init__(self):
        super().__init__()
        
        self.title("FB Scheduler Pro 2.0 - Đăng nhập")
        self.geometry("500x420")
        self.resizable(False, False)
        
        ctk.set_appearance_mode("Dark")
        
        self.colors = {
            "bg_primary": "#0F172A",
            "bg_secondary": "#1E293B",
            "accent_blue": "#3B82F6",
            "accent_green": "#10B981",
            "accent_red": "#EF4444",
            "accent_orange": "#F59E0B",
            "text_primary": "#F8FAFC",
            "text_secondary": "#94A3B8",
            "border": "#475569"
        }
        
        self.configure(fg_color=self.colors["bg_primary"])
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 420) // 2
        self.geometry(f"500x420+{x}+{y}")
        
        self.login_success = False
        self.open_admin = False
        self.saved_key_path = "temp/saved_key.json"
        
        self._create_ui()
        self._load_saved_key()
    
    def _create_ui(self):
        # Logo
        logo_frame = ctk.CTkFrame(self, fg_color=self.colors["accent_blue"], corner_radius=0, height=100)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            logo_frame,
            text="📅  FB Scheduler Pro 2.0",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        ).pack(expand=True)
        
        # Main content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=20)
        
        ctk.CTkLabel(
            content,
            text="🔑  Nhập License Key để đăng nhập",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(pady=(10, 20))
        
        # Key input
        self.ent_key = ctk.CTkEntry(
            content,
            placeholder_text="XXXX-XXXX-XXXX-XXXX",
            height=48,
            border_width=2,
            border_color=self.colors["border"],
            corner_radius=12,
            fg_color=self.colors["bg_secondary"],
            font=ctk.CTkFont(size=16),
            justify="center"
        )
        self.ent_key.pack(fill="x", pady=(0, 5))
        self.ent_key.bind("<Return>", lambda e: self._login_click())
        
        # Remember key checkbox
        self.chk_remember = ctk.CTkCheckBox(
            content,
            text="Ghi nhớ key",
            font=ctk.CTkFont(size=12),
            fg_color=self.colors["accent_green"],
            hover_color="#059669",
            corner_radius=6
        )
        self.chk_remember.pack(pady=(0, 15))
        self.chk_remember.select()
        
        # Status label
        self.lbl_status = ctk.CTkLabel(
            content,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_secondary"]
        )
        self.lbl_status.pack(pady=(0, 12))
        
        # Login button
        self.btn_login = ctk.CTkButton(
            content,
            text="🚀  Đăng nhập",
            command=self._login_click,
            height=45,
            corner_radius=12,
            fg_color=self.colors["accent_green"],
            hover_color="#059669",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.btn_login.pack(fill="x", pady=(0, 10))
        
        # Admin button (nhỏ, ở cuối)
        ctk.CTkButton(
            content,
            text="⚙️  Admin Panel",
            command=self._admin_click,
            height=32,
            corner_radius=8,
            fg_color="transparent",
            hover_color=self.colors["bg_secondary"],
            text_color=self.colors["text_secondary"],
            font=ctk.CTkFont(size=12),
            border_width=1,
            border_color=self.colors["border"]
        ).pack(pady=(0, 5))
    
    def _load_saved_key(self):
        """Load key đã lưu trước đó"""
        try:
            if os.path.exists(self.saved_key_path):
                with open(self.saved_key_path, "r") as f:
                    data = json.load(f)
                key = data.get("key", "")
                if key:
                    self.ent_key.insert(0, key)
        except:
            pass
    
    def _save_key(self, key):
        """Lưu key để dùng lại"""
        try:
            os.makedirs("temp", exist_ok=True)
            with open(self.saved_key_path, "w") as f:
                json.dump({"key": key}, f)
        except:
            pass
    
    def _login_click(self):
        key = self.ent_key.get().strip()
        if not key:
            self.lbl_status.configure(text="⚠ Vui lòng nhập key!", text_color=self.colors["accent_orange"])
            return
        
        self.btn_login.configure(state="disabled", text="⏳ Đang xác thực...")
        self.lbl_status.configure(text="🔄 Đang kết nối server...", text_color=self.colors["text_secondary"])
        
        # Validate in background thread
        def validate():
            from services.adminservices.key_service import KeyService
            service = KeyService()
            valid, msg = service.validate_key(key)
            
            self.after(0, lambda: self._on_validate_result(valid, msg, key))
        
        threading.Thread(target=validate, daemon=True).start()
    
    def _on_validate_result(self, valid, msg, key):
        self.btn_login.configure(state="normal", text="🚀  Đăng nhập")
        
        if valid:
            self.lbl_status.configure(text=f"✅ {msg}", text_color=self.colors["accent_green"])
            
            # Save key if checked
            if self.chk_remember.get():
                self._save_key(key)
            
            self.login_success = True
            self.after(800, self.destroy)
        else:
            self.lbl_status.configure(text=f"❌ {msg}", text_color=self.colors["accent_red"])
    
    def _admin_click(self):
        self.open_admin = True
        self.destroy()
