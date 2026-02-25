import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import re

class ModernMainWindow(ctk.CTk):
    def __init__(self, project):
        super().__init__()
        self.project = project
        
        self.title("FB Scheduler Pro 2.0")
        
        # Get screen size and set to 90% of screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        
        # Center window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Make resizable
        self.minsize(1400, 800)
        
        # Ultra Modern Dark Theme
        ctk.set_appearance_mode("Dark")
        
        # Premium Color Palette
        self.colors = {
            "bg_primary": "#0A0E27",       # Deep dark blue
            "bg_secondary": "#151932",     # Card background
            "accent_blue": "#3B82F6",      # Bright blue
            "accent_purple": "#8B5CF6",    # Purple
            "accent_green": "#10B981",     # Green
            "accent_red": "#EF4444",       # Red
            "accent_orange": "#F59E0B",    # Orange
            "text_primary": "#F9FAFB",     # White
            "text_secondary": "#9CA3AF",   # Gray
            "border": "#1F2937"            # Border
        }
        
        self.configure(fg_color=self.colors["bg_primary"])
        
        # Callbacks
        self.on_import_videos = None
        self.on_delete_video = None
        self.on_run_automation = None
        self.on_save_config = None
        self.on_add_page = None
        self.on_select_page = None
        self.on_delete_page = None
        self.on_rename_page = None
        self.on_add_videos = None
        
        self.video_rows = []
        self.crawler_controller = None

        self._create_modern_ui()
        
    def _create_modern_ui(self):
        # Main container
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Main
        self.grid_rowconfigure(0, weight=1)
        
        self._create_sidebar()
        self._create_main_area()
        
    def _create_sidebar(self):
        """Ultra modern sidebar with gradient effect"""
        self.sidebar = ctk.CTkFrame(
            self,
            width=350,
            corner_radius=0,
            fg_color=self.colors["bg_secondary"],
            border_width=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        # Logo Section - COMPACT
        logo_container = ctk.CTkFrame(
            self.sidebar,
            fg_color=self.colors["accent_blue"],
            corner_radius=0,
            height=80  # Giảm từ 120 xuống 80
        )
        logo_container.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        logo_container.grid_propagate(False)
        
        ctk.CTkLabel(
            logo_container,
            text="📅",
            font=ctk.CTkFont(size=32)  # Giảm từ 48
        ).pack(pady=(10, 2))
        
        ctk.CTkLabel(
            logo_container,
            text="FB Scheduler",
            font=ctk.CTkFont(size=16, weight="bold"),  # Giảm từ 22
            text_color="white"
        ).pack()
        
        ctk.CTkLabel(
            logo_container,
            text="v2.0 Pro",
            font=ctk.CTkFont(size=9),  # Giảm từ 11
            text_color="white"
        ).pack(pady=(0, 10))
        
        # Add Page Section - COMPACT
        add_section = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        add_section.grid(row=1, column=0, sticky="ew", padx=15, pady=15)  # Giảm padding
        
        ctk.CTkLabel(
            add_section,
            text="NEW PAGE",
            font=ctk.CTkFont(size=10, weight="bold"),  # Giảm từ 11
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w", pady=(0, 6))
        
        self.add_page_entry = ctk.CTkEntry(
            add_section,
            placeholder_text="Page name...",
            height=38,  # Giảm từ 45
            border_width=0,
            corner_radius=10,
            fg_color=self.colors["bg_primary"],
            font=ctk.CTkFont(size=12)
        )
        self.add_page_entry.pack(fill="x", pady=(0, 8))
        
        self.add_page_btn = ctk.CTkButton(
            add_section,
            text="➕  Add Page",
            command=self._add_page_click,
            height=38,  # Giảm từ 45
            corner_radius=10,
            fg_color=self.colors["accent_green"],
            hover_color="#059669",
            font=ctk.CTkFont(size=12, weight="bold"),
            border_width=0
        )
        self.add_page_btn.pack(fill="x")
        
        # Divider
        ctk.CTkFrame(
            self.sidebar,
            height=1,
            fg_color=self.colors["border"]
        ).grid(row=2, column=0, sticky="ew", padx=15, pady=10)  # Giảm padding
        
        # Pages Header
        pages_header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        pages_header.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 8))
        
        ctk.CTkLabel(
            pages_header,
            text="PAGES",
            font=ctk.CTkFont(size=10, weight="bold"),  # Giảm từ 11
            text_color=self.colors["text_secondary"]
        ).pack(side="left")
        
        self.page_count_badge = ctk.CTkLabel(
            pages_header,
            text="0",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="white",
            fg_color=self.colors["accent_blue"],
            corner_radius=10,
            width=28,
            height=18
        )
        self.page_count_badge.pack(side="right")
        
        # Pages List
        self.pages_scroll = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent",
            scrollbar_button_color=self.colors["accent_blue"],
            scrollbar_button_hover_color=self.colors["accent_purple"]
        )
        self.pages_scroll.grid(row=4, column=0, sticky="nsew", padx=15, pady=(0, 10))
        
        # Action Buttons Frame (Rename + Delete) - Stacked vertically
        action_btns_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        action_btns_frame.grid(row=5, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        # Rename Button
        self.rename_page_btn = ctk.CTkButton(
            action_btns_frame,
            text="✏️  Sửa tên Page",
            command=self._rename_page_click,
            height=40,
            corner_radius=10,
            fg_color=self.colors["accent_orange"],
            hover_color="#D97706",
            font=ctk.CTkFont(size=12, weight="bold"),
            border_width=0
        )
        self.rename_page_btn.pack(fill="x", pady=(0, 6))
        
        # Delete Button
        self.delete_page_btn = ctk.CTkButton(
            action_btns_frame,
            text="🗑️  Xoá Page",
            command=self._del_page_click,
            height=40,
            corner_radius=10,
            fg_color=self.colors["accent_red"],
            hover_color="#DC2626",
            font=ctk.CTkFont(size=12, weight="bold"),
            border_width=0
        )
        self.delete_page_btn.pack(fill="x")
        
    def _create_main_area(self):
        """Main content area with cards"""
        self.main_container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        
        # Make rows and columns expandable
        self.main_container.grid_rowconfigure(0, weight=0, minsize=80)   # Header - fixed
        self.main_container.grid_rowconfigure(1, weight=0, minsize=200)  # Config - COMPACT (giảm từ 300)
        self.main_container.grid_rowconfigure(2, weight=1)               # Video Queue - EXPAND
        self.main_container.grid_rowconfigure(3, weight=0, minsize=70)   # Action bar - fixed
        self.main_container.grid_rowconfigure(4, weight=0, minsize=40)   # Status - fixed
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Header with page name
        self._create_header()
        
        # Config Card
        self._create_config_card()
        
        # Video Queue Card
        self._create_video_card()
        
        # Action Bar
        self._create_action_bar()
        
        # Status Bar
        self._create_status_bar()
        
    def _create_header(self):
        """Page header with name and stats"""
        header = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent",
            height=80
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.grid_propagate(False)
        
        self.lbl_page_name = ctk.CTkLabel(
            header,
            text="Select a Page",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        self.lbl_page_name.pack(side="left", anchor="w")
        
        # Stats badges
        stats_frame = ctk.CTkFrame(header, fg_color="transparent")
        stats_frame.pack(side="right")
        
        self.video_count_label = ctk.CTkLabel(
            stats_frame,
            text="0 Videos",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white",
            fg_color=self.colors["accent_purple"],
            corner_radius=20,
            width=100,
            height=40
        )
        self.video_count_label.pack(side="left", padx=5)
        
    def _create_config_card(self):
        """Configuration card with tabs"""
        config_card = ctk.CTkFrame(
            self.main_container,
            fg_color=self.colors["bg_secondary"],
            corner_radius=20,
            border_width=1,
            border_color=self.colors["border"]
        )
        config_card.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Card Header
        card_header = ctk.CTkFrame(config_card, fg_color="transparent")
        card_header.pack(fill="x", padx=25, pady=(20, 15))
        
        ctk.CTkLabel(
            card_header,
            text="⚙️  Configuration",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(side="left")
        
        # Tabview
        self.config_tabs = ctk.CTkTabview(
            config_card,
            fg_color="transparent",
            segmented_button_fg_color=self.colors["bg_primary"],
            segmented_button_selected_color=self.colors["accent_blue"],
            segmented_button_selected_hover_color=self.colors["accent_purple"],
            corner_radius=15
        )
        self.config_tabs.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Add tabs
        self.config_tabs.add("🌐 Chrome")
        self.config_tabs.add("🔑 API")
        self.config_tabs.add("📅 Schedule")
        
        self._setup_chrome_tab()
        self._setup_api_tab()
        self._setup_schedule_tab()
        
    def _setup_chrome_tab(self):
        tab = self.config_tabs.tab("🌐 Chrome")
        
        # Tạo 2 cột để compact hơn
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        
        fields = [
            ("Chrome Binary Path", "ent_binary", "C:\\Program Files\\...", 0, 0),
            ("Profile Path", "ent_profile", "C:\\Users\\...\\Profile", 0, 1),
            ("Command Line", "ent_cmd", "--proxy-server=...", 1, 0),
            ("Page ID (Facebook)", "ent_page_id_chrome", "123456789...", 1, 1),
            ("Delay (seconds)", "ent_delay", "0", 2, 0),
            ("Note", "ent_note", "Optional notes...", 2, 1)
        ]
        
        for label, attr, placeholder, row, col in fields:
            frame = ctk.CTkFrame(tab, fg_color="transparent")
            frame.grid(row=row, column=col, sticky="ew", padx=10, pady=8)
            
            ctk.CTkLabel(
                frame,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color=self.colors["text_secondary"],
                anchor="w"
            ).pack(anchor="w", pady=(0, 5))
            
            entry = ctk.CTkEntry(
                frame,
                placeholder_text=placeholder,
                height=35,
                border_width=0,
                corner_radius=8,
                fg_color=self.colors["bg_primary"],
                font=ctk.CTkFont(size=12)
            )
            entry.pack(fill="x")
            
            attr_name = attr if attr.startswith("ent_") else f"ent_{attr}"
            setattr(self, attr_name, entry)
            
            # Bind auto-parse khi paste vào ô Chrome Binary Path
            if attr == "ent_binary":
                entry.bind("<KeyRelease>", lambda e: self.after(100, self._auto_parse_command))
                entry.bind("<<Paste>>", lambda e: self.after(200, self._auto_parse_command))
            
    def _setup_api_tab(self):
        tab = self.config_tabs.tab("🔑 API")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        
        self.chk_use_api = ctk.CTkCheckBox(
            tab,
            text="Use Facebook Graph API",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors["accent_green"],
            hover_color="#059669",
            corner_radius=8
        )
        self.chk_use_api.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(10, 15))
        
        # Page ID
        frame1 = ctk.CTkFrame(tab, fg_color="transparent")
        frame1.grid(row=1, column=0, sticky="ew", padx=10, pady=8)
        ctk.CTkLabel(frame1, text="Page ID", font=ctk.CTkFont(size=12), 
                     text_color=self.colors["text_secondary"], anchor="w").pack(anchor="w", pady=(0, 5))
        self.ent_page_id = ctk.CTkEntry(frame1, placeholder_text="123456789...", height=35, 
                                        border_width=0, corner_radius=8, 
                                        fg_color=self.colors["bg_primary"], font=ctk.CTkFont(size=12))
        self.ent_page_id.pack(fill="x")
        
        # Access Token
        frame2 = ctk.CTkFrame(tab, fg_color="transparent")
        frame2.grid(row=1, column=1, sticky="ew", padx=10, pady=8)
        ctk.CTkLabel(frame2, text="Access Token", font=ctk.CTkFont(size=12), 
                     text_color=self.colors["text_secondary"], anchor="w").pack(anchor="w", pady=(0, 5))
        self.ent_access_token = ctk.CTkEntry(frame2, placeholder_text="EAAxxxx...", height=35, 
                                             border_width=0, corner_radius=8, show="*",
                                             fg_color=self.colors["bg_primary"], font=ctk.CTkFont(size=12))
        self.ent_access_token.pack(fill="x")
        
        help_btn = ctk.CTkButton(
            tab,
            text="📖  API Setup Guide",
            fg_color=self.colors["accent_orange"],
            hover_color="#D97706",
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        help_btn.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 10))
        
    def _setup_schedule_tab(self):
        tab = self.config_tabs.tab("📅 Schedule")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_columnconfigure(2, weight=1)
        tab.grid_columnconfigure(3, weight=1)
        
        # Title
        ctk.CTkLabel(
            tab,
            text="⏰  Khung giờ đăng video cho page này",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(10, 12))
        
        # Row 1: Số video/ngày + Buổi đăng
        frame_vpd = ctk.CTkFrame(tab, fg_color="transparent")
        frame_vpd.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=6)
        ctk.CTkLabel(frame_vpd, text="Số video mỗi ngày", font=ctk.CTkFont(size=12),
                     text_color=self.colors["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.ent_vpd = ctk.CTkEntry(frame_vpd, placeholder_text="5", height=35,
                                     border_width=0, corner_radius=8,
                                     fg_color=self.colors["bg_primary"], font=ctk.CTkFont(size=12))
        self.ent_vpd.pack(fill="x")
        
        frame_period = ctk.CTkFrame(tab, fg_color="transparent")
        frame_period.grid(row=1, column=2, columnspan=2, sticky="ew", padx=10, pady=6)
        ctk.CTkLabel(frame_period, text="Buổi đăng", font=ctk.CTkFont(size=12),
                     text_color=self.colors["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.cmb_posting_period = ctk.CTkComboBox(
            frame_period,
            values=["AM (Sáng)", "PM (Chiều)", "Cả ngày"],
            height=35,
            border_width=0,
            corner_radius=8,
            fg_color=self.colors["bg_primary"],
            button_color=self.colors["accent_blue"],
            button_hover_color=self.colors["accent_purple"],
            font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=12)
        )
        self.cmb_posting_period.set("PM (Chiều)")
        self.cmb_posting_period.pack(fill="x")
        
        # Row 2: Giờ bắt đầu + Giờ kết thúc
        frame_start = ctk.CTkFrame(tab, fg_color="transparent")
        frame_start.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=6)
        ctk.CTkLabel(frame_start, text="Giờ bắt đầu (HH:MM)", font=ctk.CTkFont(size=12),
                     text_color=self.colors["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.ent_start_hour = ctk.CTkEntry(frame_start, placeholder_text="06:00", height=35,
                                           border_width=0, corner_radius=8,
                                           fg_color=self.colors["bg_primary"], font=ctk.CTkFont(size=12))
        self.ent_start_hour.pack(fill="x")
        
        frame_end = ctk.CTkFrame(tab, fg_color="transparent")
        frame_end.grid(row=2, column=2, columnspan=2, sticky="ew", padx=10, pady=6)
        ctk.CTkLabel(frame_end, text="Giờ kết thúc (HH:MM)", font=ctk.CTkFont(size=12),
                     text_color=self.colors["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.ent_end_hour = ctk.CTkEntry(frame_end, placeholder_text="10:00", height=35,
                                         border_width=0, corner_radius=8,
                                         fg_color=self.colors["bg_primary"], font=ctk.CTkFont(size=12))
        self.ent_end_hour.pack(fill="x")
        
        # Row 3: Khung giờ cụ thể (manual override)
        frame_slots = ctk.CTkFrame(tab, fg_color="transparent")
        frame_slots.grid(row=3, column=0, columnspan=4, sticky="ew", padx=10, pady=6)
        ctk.CTkLabel(frame_slots, text="Khung giờ cụ thể (tuỳ chọn, phân cách bằng dấu phẩy)", font=ctk.CTkFont(size=12),
                     text_color=self.colors["text_secondary"]).pack(anchor="w", pady=(0, 4))
        self.ent_slots = ctk.CTkEntry(frame_slots, placeholder_text="06:00, 08:00, 10:00", height=35,
                                      border_width=0, corner_radius=8,
                                      fg_color=self.colors["bg_primary"], font=ctk.CTkFont(size=12))
        self.ent_slots.pack(fill="x")
        
        # Info
        ctk.CTkLabel(
            tab,
            text="💡 Nếu điền khung giờ cụ thể, hệ thống sẽ ưu tiên dùng. Nếu để trống, sẽ tự chia đều từ giờ bắt đầu → kết thúc.",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_secondary"],
            wraplength=700
        ).grid(row=4, column=0, columnspan=4, sticky="w", padx=15, pady=(8, 10))
        
    def _create_input_field(self, parent, label, attr_name, placeholder, row, show=None):
        """Helper to create consistent input fields"""
        ctk.CTkLabel(
            parent,
            text=label,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).grid(row=row, column=0, sticky="w", padx=20, pady=(15, 5))
        
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=45,
            border_width=0,
            corner_radius=10,
            fg_color=self.colors["bg_primary"],
            font=ctk.CTkFont(size=14),
            show=show
        )
        entry.grid(row=row, column=1, sticky="ew", padx=20, pady=(15, 5))
        parent.grid_columnconfigure(1, weight=1)
        
        setattr(self, attr_name, entry)
        
    def _create_video_card(self):
        """Video queue card"""
        video_card = ctk.CTkFrame(
            self.main_container,
            fg_color=self.colors["bg_secondary"],
            corner_radius=20,
            border_width=1,
            border_color=self.colors["border"]
        )
        video_card.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        
        # Make video card expand
        video_card.grid_rowconfigure(1, weight=1)
        video_card.grid_columnconfigure(0, weight=1)
        
        # Card Header
        card_header = ctk.CTkFrame(video_card, fg_color="transparent", height=60)
        card_header.grid(row=0, column=0, sticky="ew", padx=25, pady=20)
        card_header.grid_propagate(False)
        
        ctk.CTkLabel(
            card_header,
            text="🎬  Video Queue",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(side="left")
        
        self.video_count_label = ctk.CTkLabel(
            card_header,
            text="0 Videos",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        )
        self.video_count_label.pack(side="right")
        
        # Video Scroll (TabView)
        self.video_tabview = ctk.CTkTabview(
            video_card,
            fg_color="transparent",
            segmented_button_selected_color=self.colors["accent_blue"],
            segmented_button_selected_hover_color=self.colors["accent_purple"],
            text_color=self.colors["text_primary"]
        )
        self.video_tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        tab_p1 = self.video_tabview.add("Phần 1: Có Lên Lịch")
        tab_p2 = self.video_tabview.add("Phần 2: Chỉ Đăng Cùng Lúc")
        
        tab_p1.grid_columnconfigure(0, weight=1)
        tab_p1.grid_rowconfigure(0, weight=1)
        tab_p2.grid_columnconfigure(0, weight=1)
        tab_p2.grid_rowconfigure(0, weight=1)
        
        self.video_scroll = ctk.CTkScrollableFrame(
            tab_p1,
            fg_color="transparent",
            scrollbar_button_color=self.colors["accent_blue"]
        )
        self.video_scroll.grid(row=0, column=0, sticky="nsew")
        
        self.video_scroll_p2 = ctk.CTkScrollableFrame(
            tab_p2,
            fg_color="transparent",
            scrollbar_button_color=self.colors["accent_blue"]
        )
        self.video_scroll_p2.grid(row=0, column=0, sticky="nsew")
        
        self.video_rows_p2 = []
        
    def _create_action_bar(self):
        """Action buttons bar"""
        action_bar = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent",
            height=70
        )
        action_bar.grid(row=3, column=0, sticky="ew")
        action_bar.grid_propagate(False)
        action_bar.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.import_btn = ctk.CTkButton(
            action_bar,
            text="📁  Import Videos",
            command=self._import_click,
            height=60,
            corner_radius=15,
            fg_color=self.colors["accent_blue"],
            hover_color="#2563EB",
            font=ctk.CTkFont(size=16, weight="bold"),
            border_width=0
        )
        self.import_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.save_btn = ctk.CTkButton(
            action_bar,
            text="💾  Save Config",
            command=self._save_click,
            height=60,
            corner_radius=15,
            fg_color=self.colors["accent_green"],
            hover_color="#059669",
            font=ctk.CTkFont(size=16, weight="bold"),
            border_width=0
        )
        self.save_btn.grid(row=0, column=1, sticky="ew", padx=5)
        
        self.start_btn = ctk.CTkButton(
            action_bar,
            text="🚀  START AUTOMATION",
            command=self._run_click,
            height=60,
            corner_radius=15,
            fg_color=self.colors["accent_red"],
            hover_color="#DC2626",
            font=ctk.CTkFont(size=17, weight="bold"),
            border_width=0
        )
        self.start_btn.grid(row=0, column=2, sticky="ew", padx=(10, 0))
        
    def _create_status_bar(self):
        """Status bar at bottom"""
        self.status_bar = ctk.CTkLabel(
            self.main_container,
            text="✓  Ready to start",
            height=45,
            corner_radius=12,
            fg_color=self.colors["bg_secondary"],
            font=ctk.CTkFont(size=14),
            anchor="w",
            padx=20
        )
        self.status_bar.grid(row=4, column=0, sticky="ew", pady=(20, 0))
    
    # === Event Handlers ===
    def _add_page_click(self):
        name = self.add_page_entry.get()
        if name and self.on_add_page:
            self.on_add_page(name)
            self.add_page_entry.delete(0, "end")
            
    def _del_page_click(self):
        if self.on_delete_page:
            self.on_delete_page()
    
    def _rename_page_click(self):
        """Show dialog to rename current page"""
        if not self.on_rename_page:
            return
        
        # Create a modern rename dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Sửa tên Page")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.configure(fg_color=self.colors["bg_secondary"])
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog on parent
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 200) // 2
        dialog.geometry(f"400x200+{x}+{y}")
        
        ctk.CTkLabel(
            dialog,
            text="✏️  Nhập tên mới cho Page",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(pady=(25, 15))
        
        name_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="Tên mới...",
            height=42,
            border_width=0,
            corner_radius=10,
            fg_color=self.colors["bg_primary"],
            font=ctk.CTkFont(size=14),
            width=300
        )
        name_entry.pack(pady=(0, 15))
        name_entry.focus()
        
        def do_rename():
            new_name = name_entry.get().strip()
            if new_name:
                self.on_rename_page(new_name)
                dialog.destroy()
        
        def on_enter(event):
            do_rename()
        
        name_entry.bind("<Return>", on_enter)
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="Huỷ",
            command=dialog.destroy,
            width=120,
            height=38,
            corner_radius=10,
            fg_color=self.colors["bg_primary"],
            hover_color=self.colors["border"],
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="✅  Đổi tên",
            command=do_rename,
            width=120,
            height=38,
            corner_radius=10,
            fg_color=self.colors["accent_green"],
            hover_color="#059669",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=5)

    def _import_click(self):
        if self.on_import_videos:
            self.on_import_videos()

    def _auto_parse_command(self):
        """Tự động parse khi paste cả command line vào ô Binary Path"""
        raw = self.ent_binary.get().strip()
        if not raw:
            return
        
        # Chỉ parse khi có dấu hiệu là command line đầy đủ (có -- arguments)
        if '--' not in raw:
            return
        
        # Extract binary path (phần trước arguments)
        # Pattern: "C:\path\chrome.exe" hoặc C:\path\chrome.exe
        exe_match = re.match(r'^"([^"]+\.exe)"', raw) or re.match(r'^([^\s]+\.exe)', raw)
        binary_path = exe_match.group(1) if exe_match else ''
        
        # Extract --user-data-dir
        profile_match = re.search(r'--user-data-dir="([^"]+)"', raw) or re.search(r'--user-data-dir=([^\s]+)', raw)
        profile_path = profile_match.group(1) if profile_match else ''
        
        # Command line = phần args còn lại (bỏ binary path và --user-data-dir)
        cmd_line = raw
        if exe_match:
            # Bỏ phần binary path
            cmd_line = raw[exe_match.end():].strip()
        if profile_match:
            # Bỏ --user-data-dir=...
            cmd_line = cmd_line.replace(profile_match.group(0), '').strip()
        
        # Điền vào các ô
        if binary_path:
            self.ent_binary.delete(0, 'end')
            self.ent_binary.insert(0, binary_path)
        
        if profile_path:
            self.ent_profile.delete(0, 'end')
            self.ent_profile.insert(0, profile_path)
        
        if cmd_line:
            self.ent_cmd.delete(0, 'end')
            self.ent_cmd.insert(0, cmd_line)
        
        self.log(f"✓ Auto-parse: Binary={binary_path[:40]}..., Profile={profile_path[-30:]}")
        
        # TỰ ĐỘNG LƯU sau khi parse
        self.after(500, self._save_click)

    def _save_click(self):
        if self.on_save_config:
            # Sync page_id giữa Chrome tab và API tab
            chrome_page_id = self.ent_page_id_chrome.get().strip()
            api_page_id = self.ent_page_id.get().strip()
            # Ưu tiên Chrome tab, fallback API tab
            final_page_id = chrome_page_id or api_page_id
            
            data = {
                "binary_location": self.ent_binary.get(),
                "profile_path": self.ent_profile.get(),
                "command_line": self.ent_cmd.get(),
                "page_id": final_page_id,
                "videos_per_day": self.ent_vpd.get(),
                "delay": self.ent_delay.get(),
                "note": self.ent_note.get(),
                "schedule_slots": [s.strip() for s in self.ent_slots.get().split(",") if s.strip()],
                "start_hour": self.ent_start_hour.get(),
                "end_hour": self.ent_end_hour.get(),
                "posting_period": self.cmb_posting_period.get(),
                "use_api": self.chk_use_api.get(),
                "access_token": self.ent_access_token.get()
            }
            self.on_save_config(data)

    def _run_click(self):
        if self.on_run_automation:
            self.on_run_automation()

    def _page_btn_click(self, page_data):
        if self.on_select_page:
            self.on_select_page(page_data)

    # === Controller Methods ===
    def refresh_sidebar_pages(self, pages, active_page_name=None):
        for widget in self.pages_scroll.winfo_children():
            widget.destroy()
            
        self.page_count_badge.configure(text=str(len(pages)))
            
        for p in pages:
            name = p.get("page_name", "Untitled")
            is_active = (name == active_page_name)
            
            # Truncate long names
            display_name = name if len(name) <= 22 else name[:20] + "…"
            
            btn = ctk.CTkButton(
                self.pages_scroll,
                text=f"📄 {display_name}",
                command=lambda x=p: self._page_btn_click(x),
                height=45,
                corner_radius=12,
                fg_color=self.colors["accent_blue"] if is_active else self.colors["bg_primary"],
                hover_color=self.colors["accent_purple"],
                font=ctk.CTkFont(size=12, weight="bold" if is_active else "normal"),
                anchor="w",
                border_width=0
            )
            btn.pack(fill="x", pady=4)

    def set_configuration(self, page_data):
        self.lbl_page_name.configure(text=page_data.get("page_name", "Unknown Page"))
        
        self.ent_cmd.delete(0, "end")
        self.ent_cmd.insert(0, page_data.get("command_line", ""))
        
        self.ent_page_id_chrome.delete(0, "end")
        self.ent_page_id_chrome.insert(0, page_data.get("page_id", ""))
        
        self.ent_vpd.delete(0, "end")
        self.ent_vpd.insert(0, str(page_data.get("videos_per_day", "5")))
        
        self.ent_delay.delete(0, "end")
        self.ent_delay.insert(0, str(page_data.get("delay", "0")))

        self.ent_note.delete(0, "end")
        self.ent_note.insert(0, page_data.get("note", ""))
        
        slots = page_data.get("schedule_slots", [])
        self.ent_slots.delete(0, "end")
        self.ent_slots.insert(0, ", ".join(slots))
        
        self.ent_start_hour.delete(0, "end")
        self.ent_start_hour.insert(0, page_data.get("start_hour", ""))
        
        self.ent_end_hour.delete(0, "end")
        self.ent_end_hour.insert(0, page_data.get("end_hour", ""))
        
        posting_period = page_data.get("posting_period", "PM (Chiều)")
        self.cmb_posting_period.set(posting_period)
        
        self.ent_binary.delete(0, "end")
        self.ent_binary.insert(0, page_data.get("binary_location", ""))
        
        self.ent_profile.delete(0, "end")
        self.ent_profile.insert(0, page_data.get("profile_path", ""))
        
        use_api = page_data.get("use_api", False)
        if use_api:
            self.chk_use_api.select()
        else:
            self.chk_use_api.deselect()
        
        self.ent_page_id.delete(0, "end")
        self.ent_page_id.insert(0, page_data.get("page_id", ""))
        
        self.ent_access_token.delete(0, "end")
        self.ent_access_token.insert(0, page_data.get("access_token", ""))

    def add_video_item(self, path, date_str, time_str, ampm_str):
        row_frame = ctk.CTkFrame(
            self.video_scroll,
            fg_color=self.colors["bg_primary"],
            corner_radius=8,
            height=50  # Giảm từ 70 xuống 50
        )
        row_frame.pack(fill="x", pady=3)  # Giảm pady từ 5 xuống 3
        row_frame.pack_propagate(False)
        
        # Video name - compact
        name_label = ctk.CTkLabel(
            row_frame,
            text=f"🎥 {path.split('/')[-1][:35]}...",
            font=ctk.CTkFont(size=12),  # Giảm từ 13 xuống 12
            anchor="w",
            width=280
        )
        name_label.pack(side="left", padx=10)
        
        # Date - compact
        d_ent = ctk.CTkEntry(row_frame, width=100, height=30, corner_radius=6, font=ctk.CTkFont(size=12))
        d_ent.insert(0, date_str)
        d_ent.pack(side="left", padx=3)
        
        # Time - compact
        t_ent = ctk.CTkEntry(row_frame, width=70, height=30, corner_radius=6, font=ctk.CTkFont(size=12))
        t_ent.insert(0, time_str)
        t_ent.pack(side="left", padx=3)
        
        # AM/PM - compact
        ampm_menu = ctk.CTkOptionMenu(
            row_frame,
            values=["AM", "PM"],
            width=70,
            height=30,
            corner_radius=6,
            fg_color=self.colors["accent_blue"],
            font=ctk.CTkFont(size=12)
        )
        ampm_menu.set(ampm_str)
        ampm_menu.pack(side="left", padx=3)
        
        # Delete button - compact
        del_btn = ctk.CTkButton(
            row_frame,
            text="🗑️",
            width=40,
            height=30,
            corner_radius=6,
            fg_color=self.colors["accent_red"],
            hover_color="#DC2626",
            command=lambda: self._delete_video_ui(row_frame, path),
            font=ctk.CTkFont(size=14)
        )
        del_btn.pack(side="right", padx=10)
        
        row_frame.data = {
            "path_obj": path,
            "d_ent": d_ent,
            "t_ent": t_ent,
            "ampm_menu": ampm_menu
        }
        self.video_rows.append(row_frame)
        
        # Update count
        self.video_count_label.configure(text=f"{len(self.video_rows) + len(self.video_rows_p2)} Videos")

    def _delete_video_ui(self, frame, path):
        if frame in self.video_rows:
            self.video_rows.remove(frame)
        frame.destroy()
        if self.on_delete_video:
            self.on_delete_video(path)
        self.video_count_label.configure(text=f"{len(self.video_rows) + len(self.video_rows_p2)} Videos")

    def add_video_item_part2(self, path):
        row_frame = ctk.CTkFrame(
            self.video_scroll_p2,
            fg_color=self.colors["bg_primary"],
            corner_radius=8,
            height=50
        )
        row_frame.pack(fill="x", pady=3)
        row_frame.pack_propagate(False)
        
        name_label = ctk.CTkLabel(
            row_frame,
            text=f"🎥 P2: {path.split('/')[-1][:50]}...",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        name_label.pack(side="left", padx=10)
        
        ctk.CTkLabel(
            row_frame,
            text="(Đăng Ngay)",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color=self.colors["accent_green"]
        ).pack(side="left", padx=20)
        
        del_btn = ctk.CTkButton(
            row_frame,
            text="🗑️",
            width=40,
            height=30,
            corner_radius=6,
            fg_color=self.colors["accent_red"],
            hover_color="#DC2626",
            command=lambda: self._delete_video_ui_p2(row_frame, path),
            font=ctk.CTkFont(size=14)
        )
        del_btn.pack(side="right", padx=10)
        
        row_frame.data = {"path_obj": path}
        self.video_rows_p2.append(row_frame)
        self.video_count_label.configure(text=f"{len(self.video_rows) + len(self.video_rows_p2)} Videos")

    def _delete_video_ui_p2(self, frame, path):
        if frame in self.video_rows_p2:
            self.video_rows_p2.remove(frame)
        frame.destroy()
        if self.on_delete_video:
            self.on_delete_video(path)
        self.video_count_label.configure(text=f"{len(self.video_rows) + len(self.video_rows_p2)} Videos")

    def get_video_items_data(self):
        data = []
        for widget in self.video_rows:
            if hasattr(widget, 'data'):
                d = widget.data
                data.append({
                    "path": d["path_obj"],
                    "date": d["d_ent"].get(),
                    "time": d["t_ent"].get(),
                    "ampm": d["ampm_menu"].get()
                })
        return data

    def get_video_part2_data(self):
        data = []
        for widget in self.video_rows_p2:
            if hasattr(widget, 'data'):
                data.append({
                    "path": widget.data["path_obj"],
                    "is_part2": True
                })
        return data

    def display_history(self, history):
        if not history:
            return
        last = history[-1]
        self.log(f"History: {last.get('status')} at {last.get('time_str')}")

    def update_status(self, msg):
        self.status_bar.configure(text=msg)

    def log(self, msg):
        print(f"[LOG] {msg}")
        self.status_bar.configure(text=f"📝  {msg}")

    def show_message(self, title, msg):
        messagebox.showinfo(title, msg)

    def set_processing_state(self, is_processing):
        state = "disabled" if is_processing else "normal"
        self.start_btn.configure(state=state)
        self.import_btn.configure(state=state)
        self.save_btn.configure(state=state)
