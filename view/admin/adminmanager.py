import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import pyperclip


class AdminManagerWindow(ctk.CTk):
    """Admin UI để quản lý License Keys"""
    
    def __init__(self):
        super().__init__()
        
        self.title("🔑 Admin - License Key Manager")
        self.geometry("1100x750")
        self.minsize(900, 600)
        
        ctk.set_appearance_mode("Dark")
        
        # Color palette
        self.colors = {
            "bg_primary": "#0F172A",
            "bg_secondary": "#1E293B",
            "bg_card": "#334155",
            "accent_blue": "#3B82F6",
            "accent_green": "#10B981",
            "accent_red": "#EF4444",
            "accent_orange": "#F59E0B",
            "accent_purple": "#8B5CF6",
            "text_primary": "#F8FAFC",
            "text_secondary": "#94A3B8",
            "border": "#475569",
            "success": "#22C55E",
            "warning": "#EAB308"
        }
        
        self.configure(fg_color=self.colors["bg_primary"])
        
        # Callbacks
        self.on_connect = None
        self.on_add_key = None
        self.on_delete_key = None
        self.on_toggle_key = None
        self.on_edit_key = None
        self.on_refresh = None
        
        self._create_ui()
    
    def _create_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self._create_header()
        self._create_add_key_section()
        self._create_key_list()
        self._create_log_bar()
    
    def _create_header(self):
        """Header với GitHub token và kết nối"""
        header = ctk.CTkFrame(self, fg_color=self.colors["bg_secondary"], corner_radius=0, height=120)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)
        
        # Title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=25, pady=(15, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="🔑  Admin - License Key Manager",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(side="left")
        
        # Refresh button
        ctk.CTkButton(
            title_frame,
            text="🔄 Refresh",
            command=lambda: self.on_refresh() if self.on_refresh else None,
            width=100,
            height=32,
            corner_radius=8,
            fg_color=self.colors["accent_purple"],
            hover_color="#7C3AED",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="right")
        
        # Token row
        token_frame = ctk.CTkFrame(header, fg_color="transparent")
        token_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=25, pady=(0, 15))
        token_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            token_frame,
            text="GitHub Token:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).grid(row=0, column=0, padx=(0, 10))
        
        self.ent_token = ctk.CTkEntry(
            token_frame,
            placeholder_text="ghp_xxxxxxxxxxxxxxxxxxxx",
            height=36,
            border_width=0,
            corner_radius=8,
            fg_color=self.colors["bg_primary"],
            font=ctk.CTkFont(size=12),
            show="•"
        )
        self.ent_token.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        # Show/Hide toggle
        self.show_token = False
        self.btn_toggle_token = ctk.CTkButton(
            token_frame,
            text="👁",
            command=self._toggle_token_visibility,
            width=36,
            height=36,
            corner_radius=8,
            fg_color=self.colors["bg_card"],
            hover_color=self.colors["border"]
        )
        self.btn_toggle_token.grid(row=0, column=2, padx=(0, 10))
        
        ctk.CTkButton(
            token_frame,
            text="🔗  Kết nối GitHub",
            command=self._connect_click,
            width=160,
            height=36,
            corner_radius=8,
            fg_color=self.colors["accent_blue"],
            hover_color="#2563EB",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=3)
    
    def _toggle_token_visibility(self):
        self.show_token = not self.show_token
        self.ent_token.configure(show="" if self.show_token else "•")
        self.btn_toggle_token.configure(text="🙈" if self.show_token else "👁")
    
    def _create_add_key_section(self):
        """Section tạo key mới"""
        section = ctk.CTkFrame(self, fg_color=self.colors["bg_secondary"], corner_radius=15)
        section.grid(row=1, column=0, sticky="ew", padx=20, pady=(15, 10))
        section.grid_columnconfigure(1, weight=1)
        
        # Title
        ctk.CTkLabel(
            section,
            text="➕  Tạo Key Mới",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=20, pady=(15, 12))
        
        # Ghi chú
        ctk.CTkLabel(
            section,
            text="Ghi chú:",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"]
        ).grid(row=1, column=0, padx=(20, 8), pady=(0, 15))
        
        self.ent_note = ctk.CTkEntry(
            section,
            placeholder_text="Tên khách hàng, mục đích...",
            height=36,
            border_width=0,
            corner_radius=8,
            fg_color=self.colors["bg_primary"],
            font=ctk.CTkFont(size=12)
        )
        self.ent_note.grid(row=1, column=1, sticky="ew", padx=5, pady=(0, 15))
        
        # Số ngày
        ctk.CTkLabel(
            section,
            text="Số ngày:",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"]
        ).grid(row=1, column=2, padx=(15, 8), pady=(0, 15))
        
        self.ent_days = ctk.CTkEntry(
            section,
            placeholder_text="30",
            width=80,
            height=36,
            border_width=0,
            corner_radius=8,
            fg_color=self.colors["bg_primary"],
            font=ctk.CTkFont(size=12)
        )
        self.ent_days.insert(0, "30")
        self.ent_days.grid(row=1, column=3, padx=5, pady=(0, 15))
        
        # Tạo button
        ctk.CTkButton(
            section,
            text="🔑  Tạo Key",
            command=self._add_key_click,
            width=120,
            height=36,
            corner_radius=8,
            fg_color=self.colors["accent_green"],
            hover_color="#059669",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=1, column=4, padx=(10, 20), pady=(0, 15))
    
    def _create_key_list(self):
        """Danh sách keys"""
        list_frame = ctk.CTkFrame(self, fg_color=self.colors["bg_secondary"], corner_radius=15)
        list_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=5)
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="📋  Danh Sách License Keys",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(side="left")
        
        self.lbl_key_count = ctk.CTkLabel(
            header_frame,
            text="0 keys",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white",
            fg_color=self.colors["accent_blue"],
            corner_radius=12,
            width=80,
            height=28
        )
        self.lbl_key_count.pack(side="right")
        
        # Column headers
        col_header = ctk.CTkFrame(list_frame, fg_color=self.colors["bg_card"], corner_radius=8, height=36)
        col_header.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 5))
        col_header.grid_propagate(False)
        col_header.grid_columnconfigure(0, weight=3)  # Key
        col_header.grid_columnconfigure(1, weight=1)  # Status
        col_header.grid_columnconfigure(2, weight=1)  # Created
        col_header.grid_columnconfigure(3, weight=1)  # Expires
        col_header.grid_columnconfigure(4, weight=2)  # Note
        col_header.grid_columnconfigure(5, weight=2)  # Actions
        
        headers = ["Key", "Trạng thái", "Ngày tạo", "Hết hạn", "Ghi chú", "Thao tác"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                col_header,
                text=h,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.colors["text_secondary"]
            ).grid(row=0, column=i, sticky="w", padx=10, pady=5)
        
        # Scrollable key list
        self.key_scroll = ctk.CTkScrollableFrame(
            list_frame,
            fg_color="transparent",
            scrollbar_button_color=self.colors["accent_blue"],
            scrollbar_button_hover_color=self.colors["accent_purple"]
        )
        self.key_scroll.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.key_scroll.grid_columnconfigure(0, weight=1)
    
    def _create_log_bar(self):
        """Log bar ở dưới"""
        self.lbl_log = ctk.CTkLabel(
            self,
            text="📝 Sẵn sàng - Nhập GitHub Token để bắt đầu",
            height=40,
            corner_radius=10,
            fg_color=self.colors["bg_secondary"],
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_secondary"],
            anchor="w",
            padx=20
        )
        self.lbl_log.grid(row=3, column=0, sticky="ew", padx=20, pady=(5, 15))
    
    # === Event Handlers ===
    def _connect_click(self):
        token = self.ent_token.get().strip()
        if self.on_connect:
            self.on_connect(token)
    
    def _add_key_click(self):
        note = self.ent_note.get().strip()
        days = self.ent_days.get().strip() or "30"
        if self.on_add_key:
            self.on_add_key(note, days)
            self.ent_note.delete(0, "end")
    
    # === Public Methods ===
    def set_token(self, token):
        self.ent_token.delete(0, "end")
        self.ent_token.insert(0, token)
    
    def log(self, msg):
        self.lbl_log.configure(text=f"📝 {msg}")
        print(f"[ADMIN] {msg}")
    
    def display_keys(self, keys):
        """Hiển thị danh sách keys"""
        # Clear old
        for widget in self.key_scroll.winfo_children():
            widget.destroy()
        
        self.lbl_key_count.configure(text=f"{len(keys)} keys")
        
        for i, k in enumerate(keys):
            self._create_key_row(k, i)
    
    def _create_key_row(self, key_data, index):
        """Tạo 1 hàng key"""
        is_active = key_data.get("status") == "active"
        bg = self.colors["bg_primary"] if index % 2 == 0 else self.colors["bg_card"]
        
        row = ctk.CTkFrame(self.key_scroll, fg_color=bg, corner_radius=8, height=45)
        row.pack(fill="x", pady=2)
        row.pack_propagate(False)
        row.grid_columnconfigure(0, weight=3)
        row.grid_columnconfigure(1, weight=1)
        row.grid_columnconfigure(2, weight=1)
        row.grid_columnconfigure(3, weight=1)
        row.grid_columnconfigure(4, weight=2)
        row.grid_columnconfigure(5, weight=2)
        
        key_val = key_data.get("key", "")
        
        # Key (clickable to copy)
        key_btn = ctk.CTkButton(
            row,
            text=key_val,
            command=lambda k=key_val: self._copy_key(k),
            fg_color="transparent",
            hover_color=self.colors["accent_blue"],
            text_color=self.colors["accent_blue"] if is_active else self.colors["accent_red"],
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
            height=30
        )
        key_btn.grid(row=0, column=0, sticky="w", padx=8)
        
        # Status
        status_text = "✅ Active" if is_active else "❌ Disabled"
        status_color = self.colors["success"] if is_active else self.colors["accent_red"]
        ctk.CTkLabel(
            row,
            text=status_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=status_color
        ).grid(row=0, column=1, sticky="w", padx=5)
        
        # Created
        ctk.CTkLabel(
            row,
            text=key_data.get("created_at", ""),
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_secondary"]
        ).grid(row=0, column=2, sticky="w", padx=5)
        
        # Expires
        expires = key_data.get("expires_at", "")
        ctk.CTkLabel(
            row,
            text=expires,
            font=ctk.CTkFont(size=11),
            text_color=self.colors["warning"] if expires else self.colors["text_secondary"]
        ).grid(row=0, column=3, sticky="w", padx=5)
        
        # Note
        ctk.CTkLabel(
            row,
            text=key_data.get("note", "")[:20],
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_secondary"]
        ).grid(row=0, column=4, sticky="w", padx=5)
        
        # Actions
        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.grid(row=0, column=5, sticky="e", padx=5)
        
        # Toggle button
        toggle_text = "🔒" if is_active else "🔓"
        ctk.CTkButton(
            actions,
            text=toggle_text,
            command=lambda k=key_val: self._toggle_click(k),
            width=32,
            height=28,
            corner_radius=6,
            fg_color=self.colors["accent_orange"],
            hover_color="#D97706",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=2)
        
        # Edit button
        ctk.CTkButton(
            actions,
            text="✏️",
            command=lambda k=key_val, n=key_data.get("note", ""): self._edit_click(k, n),
            width=32,
            height=28,
            corner_radius=6,
            fg_color=self.colors["accent_purple"],
            hover_color="#7C3AED",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=2)
        
        # Delete button
        ctk.CTkButton(
            actions,
            text="🗑️",
            command=lambda k=key_val: self._delete_click(k),
            width=32,
            height=28,
            corner_radius=6,
            fg_color=self.colors["accent_red"],
            hover_color="#DC2626",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=2)
        
        # Copy button
        ctk.CTkButton(
            actions,
            text="📋",
            command=lambda k=key_val: self._copy_key(k),
            width=32,
            height=28,
            corner_radius=6,
            fg_color=self.colors["accent_blue"],
            hover_color="#2563EB",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=2)
    
    def _copy_key(self, key):
        try:
            pyperclip.copy(key)
            self.log(f"📋 Đã copy key: {key}")
        except:
            # Fallback nếu không có pyperclip
            self.clipboard_clear()
            self.clipboard_append(key)
            self.log(f"📋 Đã copy key: {key}")
    
    def _toggle_click(self, key):
        if self.on_toggle_key:
            self.on_toggle_key(key)
    
    def _delete_click(self, key):
        confirm = messagebox.askyesno(
            "Xác nhận xoá",
            f"Bạn có chắc muốn xoá key:\n{key}?"
        )
        if confirm and self.on_delete_key:
            self.on_delete_key(key)
    
    def _edit_click(self, key, current_note):
        """Mở dialog sửa key"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Sửa Key")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.configure(fg_color=self.colors["bg_secondary"])
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 250) // 2
        dialog.geometry(f"400x250+{x}+{y}")
        
        ctk.CTkLabel(
            dialog,
            text=f"✏️  Sửa Key: {key[:15]}...",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(pady=(20, 15))
        
        # Note
        ctk.CTkLabel(dialog, text="Ghi chú mới:", font=ctk.CTkFont(size=12),
                     text_color=self.colors["text_secondary"]).pack(anchor="w", padx=30)
        ent_new_note = ctk.CTkEntry(dialog, placeholder_text="Ghi chú...", height=36,
                                     border_width=0, corner_radius=8,
                                     fg_color=self.colors["bg_primary"], width=340)
        ent_new_note.pack(pady=(5, 10))
        ent_new_note.insert(0, current_note)
        
        # Days
        ctk.CTkLabel(dialog, text="Gia hạn thêm (ngày):", font=ctk.CTkFont(size=12),
                     text_color=self.colors["text_secondary"]).pack(anchor="w", padx=30)
        ent_new_days = ctk.CTkEntry(dialog, placeholder_text="30", height=36,
                                     border_width=0, corner_radius=8,
                                     fg_color=self.colors["bg_primary"], width=340)
        ent_new_days.pack(pady=(5, 15))
        
        def do_edit():
            if self.on_edit_key:
                self.on_edit_key(key, ent_new_note.get(), ent_new_days.get())
            dialog.destroy()
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack()
        
        ctk.CTkButton(
            btn_frame, text="Huỷ", command=dialog.destroy,
            width=100, height=34, corner_radius=8,
            fg_color=self.colors["bg_card"], hover_color=self.colors["border"]
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame, text="✅ Lưu", command=do_edit,
            width=100, height=34, corner_radius=8,
            fg_color=self.colors["accent_green"], hover_color="#059669",
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=5)


# === Chạy Admin độc lập ===
if __name__ == "__main__":
    import sys
    import os
    # Thêm root vào path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    
    from controoller.admin.admin_controller import AdminController
    
    app = AdminManagerWindow()
    controller = AdminController(app)
    app.mainloop()
