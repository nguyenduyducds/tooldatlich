import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class MainWindow(ctk.CTk):
    def __init__(self, project):
        super().__init__()
        self.project = project
        
        self.title("FB Scheduler Pro")
        self.geometry("1400x900")
        
        # Modern color scheme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # Custom colors
        self.colors = {
            "primary": "#1877F2",      # Facebook blue
            "secondary": "#42B72A",    # Green
            "danger": "#E4405F",       # Red
            "warning": "#FFA500",      # Orange
            "dark": "#18191A",         # Dark background
            "card": "#242526",         # Card background
            "border": "#3A3B3C",       # Border
            "text": "#E4E6EB",         # Text
            "text_secondary": "#B0B3B8" # Secondary text
        }
        
        # Callbacks (assigned by Controller)
        self.on_import_videos = None
        self.on_delete_video = None
        self.on_run_automation = None
        self.on_generate_port = None
        self.on_save_config = None
        self.on_add_page = None
        self.on_select_page = None
        self.on_delete_page = None
        self.on_add_videos = None
        
        self.crawler_controller = None
        self.video_rows = []

        self._setup_modern_layout()
        
    def _setup_modern_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Modern Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(
            self, 
            width=280, 
            corner_radius=0,
            fg_color=self.colors["card"]
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar_frame.grid_rowconfigure(3, weight=1)

        # Logo with icon
        self.logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, padx=20, pady=(30, 20), sticky="ew")
        
        self.logo_label = ctk.CTkLabel(
            self.logo_frame, 
            text="📅 FB Scheduler", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors["primary"]
        )
        self.logo_label.pack()
        
        self.subtitle_label = ctk.CTkLabel(
            self.logo_frame,
            text="Professional Video Manager",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"]
        )
        self.subtitle_label.pack()
        
        # Add Page Section
        self.add_page_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.add_page_frame.grid(row=1, column=0, padx=15, pady=(10, 5), sticky="ew")
        
        self.add_page_entry = ctk.CTkEntry(
            self.add_page_frame, 
            placeholder_text="🆕 New Page Name",
            height=40,
            border_width=2,
            corner_radius=10
        )
        self.add_page_entry.pack(fill="x", pady=(0, 8))
        
        self.add_page_btn = ctk.CTkButton(
            self.add_page_frame, 
            text="➕ Add Page",
            command=self._add_page_click,
            height=40,
            corner_radius=10,
            fg_color=self.colors["secondary"],
            hover_color="#36A420"
        )
        self.add_page_btn.pack(fill="x")
        
        # Divider
        ctk.CTkFrame(self.sidebar_frame, height=2, fg_color=self.colors["border"]).grid(
            row=2, column=0, sticky="ew", padx=20, pady=15
        )
        
        # Pages List
        self.pages_scroll = ctk.CTkScrollableFrame(
            self.sidebar_frame, 
            label_text="📄 Your Pages",
            label_font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            label_fg_color=self.colors["card"]
        )
        self.pages_scroll.grid(row=3, column=0, sticky="nsew", padx=15, pady=(0, 10))
        
        # Delete Page Button
        self.delete_page_btn = ctk.CTkButton(
            self.sidebar_frame, 
            text="🗑️ Delete Page",
            fg_color=self.colors["danger"],
            hover_color="#C13584",
            command=self._del_page_click,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.delete_page_btn.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

        # --- Main Content Area ---
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.main_area.grid_rowconfigure(1, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)

        # Header Card
        self.header_card = ctk.CTkFrame(
            self.main_area,
            fg_color=self.colors["card"],
            corner_radius=15
        )
        self.header_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # Config Panel (Tabview)
        self.config_tabview = ctk.CTkTabview(
            self.header_card,
            corner_radius=10,
            fg_color=self.colors["card"]
        )
        self.config_tabview.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Tabs
        self.config_tabview.add("⚙️ Settings")
        self.config_tabview.add("🔑 API Config")
        self.config_tabview.add("📊 Schedule")
        
        self._create_settings_tab()
        self._create_api_tab()
        self._create_schedule_tab()
        
        # Video Queue Card
        self.video_card = ctk.CTkFrame(
            self.main_area,
            fg_color=self.colors["card"],
            corner_radius=15
        )
        self.video_card.grid(row=1, column=0, sticky="nsew")
        self.video_card.grid_rowconfigure(1, weight=1)
        self.video_card.grid_columnconfigure(0, weight=1)
        
        # Video Header
        self.video_header = ctk.CTkFrame(self.video_card, fg_color="transparent")
        self.video_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        self.vf_label = ctk.CTkLabel(
            self.video_header, 
            text="🎬 Video Queue",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["text"]
        )
        self.vf_label.pack(side="left")
        
        self.video_count_label = ctk.CTkLabel(
            self.video_header,
            text="0 videos",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        )
        self.video_count_label.pack(side="left", padx=(10, 0))
        
        # Video Scroll
        self.video_scroll = ctk.CTkScrollableFrame(
            self.video_card,
            fg_color="transparent"
        )
        self.video_scroll.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        # Action Buttons
        self.btn_frame = ctk.CTkFrame(self.main_area, fg_color="transparent", height=70)
        self.btn_frame.grid(row=2, column=0, sticky="ew", pady=(15, 0))
        
        self.import_btn = ctk.CTkButton(
            self.btn_frame, 
            text="📁 Import Videos",
            command=self._import_click,
            height=50,
            corner_radius=12,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.colors["primary"],
            hover_color="#1565C0"
        )
        self.import_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        self.save_btn = ctk.CTkButton(
            self.btn_frame, 
            text="💾 Save Config",
            command=self._save_click,
            fg_color=self.colors["secondary"],
            hover_color="#36A420",
            height=50,
            corner_radius=12,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.save_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        self.start_btn = ctk.CTkButton(
            self.btn_frame, 
            text="🚀 START AUTOMATION",
            command=self._run_click,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            corner_radius=12,
            fg_color=self.colors["danger"],
            hover_color="#C13584"
        )
        self.start_btn.pack(side="right", fill="x", expand=True)

        # Status Bar
        self.status_bar = ctk.CTkLabel(
            self,
            text="✓ Ready",
            anchor="w",
            height=35,
            fg_color=self.colors["card"],
            corner_radius=8,
            font=ctk.CTkFont(size=13)
        )
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 10))

    
    def _create_settings_tab(self):
        """Tab Settings - Chrome/Profile config"""
        tab = self.config_tabview.tab("⚙️ Settings")
        
        # Page Name Display
        self.lbl_page_name = ctk.CTkLabel(
            tab, 
            text="No Page Selected",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.colors["primary"]
        )
        self.lbl_page_name.grid(row=0, column=0, columnspan=4, pady=(10, 20), sticky="w", padx=15)
        
        # Chrome Path
        ctk.CTkLabel(tab, text="🌐 Chrome Path:", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=1, column=0, sticky="w", padx=15, pady=(5, 2))
        self.ent_binary = ctk.CTkEntry(tab, height=35, corner_radius=8)
        self.ent_binary.grid(row=2, column=0, columnspan=4, sticky="ew", padx=15, pady=(0, 10))
        
        # Profile Path
        ctk.CTkLabel(tab, text="👤 Profile Path:", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=3, column=0, sticky="w", padx=15, pady=(5, 2))
        self.ent_profile = ctk.CTkEntry(tab, height=35, corner_radius=8)
        self.ent_profile.grid(row=4, column=0, columnspan=4, sticky="ew", padx=15, pady=(0, 10))
        
        # Command Line
        ctk.CTkLabel(tab, text="⌨️ Command Line:", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=5, column=0, sticky="w", padx=15, pady=(5, 2))
        self.ent_cmd = ctk.CTkEntry(tab, height=35, corner_radius=8)
        self.ent_cmd.grid(row=6, column=0, columnspan=4, sticky="ew", padx=15, pady=(0, 10))
        
        # Port & Delay
        port_delay_frame = ctk.CTkFrame(tab, fg_color="transparent")
        port_delay_frame.grid(row=7, column=0, columnspan=4, sticky="ew", padx=15, pady=(5, 10))
        port_delay_frame.grid_columnconfigure((0, 1), weight=1)
        
        port_frame = ctk.CTkFrame(port_delay_frame, fg_color="transparent")
        port_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(port_frame, text="🔌 Port:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")
        self.ent_port = ctk.CTkEntry(port_frame, height=35, corner_radius=8)
        self.ent_port.pack(fill="x", pady=(2, 0))
        
        delay_frame = ctk.CTkFrame(port_delay_frame, fg_color="transparent")
        delay_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(delay_frame, text="⏱️ Delay (s):", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")
        self.ent_delay = ctk.CTkEntry(delay_frame, height=35, corner_radius=8)
        self.ent_delay.pack(fill="x", pady=(2, 0))
        
        # Note
        ctk.CTkLabel(tab, text="📝 Note:", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=8, column=0, sticky="w", padx=15, pady=(5, 2))
        self.ent_note = ctk.CTkEntry(tab, height=35, corner_radius=8)
        self.ent_note.grid(row=9, column=0, columnspan=4, sticky="ew", padx=15, pady=(0, 15))
        
        tab.grid_columnconfigure(0, weight=1)
    
    def _create_api_tab(self):
        """Tab API Config"""
        tab = self.config_tabview.tab("🔑 API Config")
        
        # Use API Checkbox
        self.chk_use_api = ctk.CTkCheckBox(
            tab,
            text="Use Facebook Graph API (instead of Selenium)",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8
        )
        self.chk_use_api.grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(15, 20))
        
        # Page ID
        ctk.CTkLabel(tab, text="🆔 Page ID:", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=1, column=0, sticky="w", padx=15, pady=(5, 2))
        self.ent_page_id = ctk.CTkEntry(
            tab,
            placeholder_text="123456789...",
            height=35,
            corner_radius=8
        )
        self.ent_page_id.grid(row=2, column=0, columnspan=4, sticky="ew", padx=15, pady=(0, 10))
        
        # Access Token
        ctk.CTkLabel(tab, text="🔐 Access Token:", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=3, column=0, sticky="w", padx=15, pady=(5, 2))
        self.ent_access_token = ctk.CTkEntry(
            tab,
            placeholder_text="EAAxxxx...",
            show="*",
            height=35,
            corner_radius=8
        )
        self.ent_access_token.grid(row=4, column=0, columnspan=4, sticky="ew", padx=15, pady=(0, 10))
        
        # Help text
        help_text = ctk.CTkLabel(
            tab,
            text="💡 Tip: Check FACEBOOK_API_GUIDE.md for setup instructions",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"]
        )
        help_text.grid(row=5, column=0, columnspan=4, sticky="w", padx=15, pady=(10, 15))
        
        tab.grid_columnconfigure(0, weight=1)
    
    def _create_schedule_tab(self):
        """Tab Schedule Config"""
        tab = self.config_tabview.tab("📊 Schedule")
        
        # Videos Per Day
        ctk.CTkLabel(tab, text="📹 Videos Per Day:", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=15, pady=(15, 2))
        self.ent_vpd = ctk.CTkEntry(tab, height=35, corner_radius=8)
        self.ent_vpd.grid(row=1, column=0, columnspan=4, sticky="ew", padx=15, pady=(0, 10))
        
        # Schedule Slots
        ctk.CTkLabel(tab, text="🕐 Schedule Slots (HH:MM, comma separated):", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=2, column=0, sticky="w", padx=15, pady=(5, 2))
        self.ent_slots = ctk.CTkEntry(
            tab,
            placeholder_text="09:00, 12:00, 15:00, 18:00",
            height=35,
            corner_radius=8
        )
        self.ent_slots.grid(row=3, column=0, columnspan=4, sticky="ew", padx=15, pady=(0, 10))
        
        # Example
        example_text = ctk.CTkLabel(
            tab,
            text="Example: 09:00, 12:00, 15:00 → Videos will cycle through these times",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"]
        )
        example_text.grid(row=4, column=0, columnspan=4, sticky="w", padx=15, pady=(5, 15))
        
        tab.grid_columnconfigure(0, weight=1)
        # Using grid in config_frame
        cf = self.config_frame
        
        # Page Name Display
        self.lbl_page_name = ctk.CTkLabel(cf, text="No Page Selected", font=ctk.CTkFont(size=20))
        self.lbl_page_name.grid(row=0, column=0, columnspan=4, pady=10, sticky="w", padx=10)
        
        # Command Line / Profile
        ctk.CTkLabel(cf, text="Cmd Line / Profile:").grid(row=1, column=0, sticky="e", padx=5)
        self.ent_cmd = ctk.CTkEntry(cf, width=300)
        self.ent_cmd.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5)
        
        # Port
        ctk.CTkLabel(cf, text="Port:").grid(row=1, column=3, sticky="e", padx=5)
        self.ent_port = ctk.CTkEntry(cf, width=80)
        self.ent_port.grid(row=1, column=4, sticky="w", padx=5)
        
        # Videos Per Day
        ctk.CTkLabel(cf, text="Videos/Day:").grid(row=2, column=0, sticky="e", padx=5)
        self.ent_vpd = ctk.CTkEntry(cf, width=60)
        self.ent_vpd.grid(row=2, column=1, sticky="w", padx=5)
        
        # Delay
        ctk.CTkLabel(cf, text="Delay (s):").grid(row=2, column=2, sticky="e", padx=5)
        self.ent_delay = ctk.CTkEntry(cf, width=60)
        self.ent_delay.grid(row=2, column=3, sticky="w", padx=5)
        
        # Slots (comma sep)
        ctk.CTkLabel(cf, text="Slots (HH:MM):").grid(row=3, column=0, sticky="e", padx=5)
        self.ent_slots = ctk.CTkEntry(cf, width=400)
        self.ent_slots.grid(row=3, column=1, columnspan=4, sticky="ew", padx=5, pady=5)
        
        # Note
        ctk.CTkLabel(cf, text="Note:").grid(row=4, column=0, sticky="e", padx=5)
        self.ent_note = ctk.CTkEntry(cf, width=400)
        self.ent_note.grid(row=4, column=1, columnspan=4, sticky="ew", padx=5, pady=5)

        # Binary Path (Auto-parsed)
        ctk.CTkLabel(cf, text="Chrome Path:").grid(row=5, column=0, sticky="e", padx=5)
        self.ent_binary = ctk.CTkEntry(cf, width=400)
        self.ent_binary.grid(row=5, column=1, columnspan=4, sticky="ew", padx=5, pady=5)
        
        # Profile Path (Auto-parsed)
        ctk.CTkLabel(cf, text="Profile Path:").grid(row=6, column=0, sticky="e", padx=5)
        self.ent_profile = ctk.CTkEntry(cf, width=400)
        self.ent_profile.grid(row=6, column=1, columnspan=4, sticky="ew", padx=5, pady=5)
        
        # --- API Mode Fields ---
        ctk.CTkLabel(cf, text="─── Facebook API (Alternative) ───", font=ctk.CTkFont(size=12, weight="bold")).grid(row=7, column=0, columnspan=5, pady=(10,5))
        
        # Use API Mode
        self.chk_use_api = ctk.CTkCheckBox(cf, text="Dùng Facebook Graph API (thay vì Selenium)")
        self.chk_use_api.grid(row=8, column=0, columnspan=5, sticky="w", padx=10, pady=5)
        
        # Page ID
        ctk.CTkLabel(cf, text="Page ID:").grid(row=9, column=0, sticky="e", padx=5)
        self.ent_page_id = ctk.CTkEntry(cf, width=200, placeholder_text="123456789...")
        self.ent_page_id.grid(row=9, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Access Token
        ctk.CTkLabel(cf, text="Access Token:").grid(row=10, column=0, sticky="e", padx=5)
        self.ent_access_token = ctk.CTkEntry(cf, width=400, placeholder_text="EAAxxxx...", show="*")
        self.ent_access_token.grid(row=10, column=1, columnspan=4, sticky="ew", padx=5, pady=5)


    # --- Methods called by internal UI events ---
    def _add_page_click(self):
        name = self.add_page_entry.get()
        if name and self.on_add_page:
            self.on_add_page(name)
            self.add_page_entry.delete(0, "end")
            
    def _del_page_click(self):
        if self.on_delete_page:
            self.on_delete_page()

    def _import_click(self):
        if self.on_import_videos:
            self.on_import_videos()

    def _save_click(self):
        if self.on_save_config:
            # Gather data
            data = {
                "command_line": self.ent_cmd.get(),
                "port": self.ent_port.get(),
                "videos_per_day": self.ent_vpd.get(),
                "delay": self.ent_delay.get(),
                "note": self.ent_note.get(),
                # Parse slots
                "schedule_slots": [s.strip() for s in self.ent_slots.get().split(",") if s.strip()],
                # API fields
                "use_api": self.chk_use_api.get(),
                "page_id": self.ent_page_id.get(),
                "access_token": self.ent_access_token.get()
            }
            self.on_save_config(data)

    def _run_click(self):
        if self.on_run_automation:
            self.on_run_automation()

    def _page_btn_click(self, page_data):
        if self.on_select_page:
            self.on_select_page(page_data)

    # --- Methods called by Controller ---
    def refresh_sidebar_pages(self, pages, active_page_name=None):
        # Clear existing
        for widget in self.pages_scroll.winfo_children():
            widget.destroy()
            
        for p in pages:
            name = p.get("page_name", "Untitled")
            fg = "green" if name == active_page_name else "transparent"
            btn = ctk.CTkButton(self.pages_scroll, text=name, fg_color=fg, anchor="w",
                                command=lambda x=p: self._page_btn_click(x))
            btn.pack(fill="x", pady=2)

    def set_configuration(self, page_data):
        self.lbl_page_name.configure(text=page_data.get("page_name", "Unknown Page"))
        
        self.ent_cmd.delete(0, "end")
        self.ent_cmd.insert(0, page_data.get("command_line", ""))
        
        self.ent_port.delete(0, "end")
        self.ent_port.insert(0, str(page_data.get("port", "")))
        
        self.ent_vpd.delete(0, "end")
        self.ent_vpd.insert(0, str(page_data.get("videos_per_day", "5")))
        
        self.ent_delay.delete(0, "end")
        self.ent_delay.insert(0, str(page_data.get("delay", "0")))

        self.ent_note.delete(0, "end")
        self.ent_note.insert(0, page_data.get("note", ""))
        
        slots = page_data.get("schedule_slots", [])
        self.ent_slots.delete(0, "end")
        self.ent_slots.insert(0, ", ".join(slots))
        
        self.ent_binary.delete(0, "end")
        self.ent_binary.insert(0, page_data.get("binary_location", ""))
        
        self.ent_profile.delete(0, "end")
        self.ent_profile.insert(0, page_data.get("profile_path", ""))
        
        # API fields
        use_api = page_data.get("use_api", False)
        if use_api:
            self.chk_use_api.select()
        else:
            self.chk_use_api.deselect()
        
        self.ent_page_id.delete(0, "end")
        self.ent_page_id.insert(0, page_data.get("page_id", ""))
        
        self.ent_access_token.delete(0, "end")
        self.ent_access_token.insert(0, page_data.get("access_token", ""))

        
        # Clear video list if switching page? 
        # Controller calls load_config -> select_page. 
        # Does controller manage video list per page?
        # NO. Controller uses self.project.video_items.
        # This implies video items are GLOBAL for the project, not per page?
        # But user selects a page (config) and then likely imports videos to schedule for THAT page.
        # The code in Controller `add_videos` gets `current_page["schedule_slots"]` to calculate dates.
        # So the video list *is* global in memory, but maybe intended to be transient?
        # I'll just clear the UI video list and let the user import. 
        # Wait, if I switch pages, should I clear the queue?
        # The controller doesn't clear `self.project.video_items` on page switch.
        # So the queue is global.
        pass

    def add_video_item(self, path, date_str, time_str, ampm_str):
        # Add a row to video_scroll
        # We need to track them to get_video_items_data later
        row_frame = ctk.CTkFrame(self.video_scroll)
        row_frame.pack(fill="x", pady=2)
        
        ctk.CTkLabel(row_frame, text=path.split("/")[-1], width=200, anchor="w").pack(side="left", padx=5)
        
        d_ent = ctk.CTkEntry(row_frame, width=100)
        d_ent.insert(0, date_str)
        d_ent.pack(side="left", padx=2)
        
        t_ent = ctk.CTkEntry(row_frame, width=60)
        t_ent.insert(0, time_str)
        t_ent.pack(side="left", padx=2)
        
        ampm_menu = ctk.CTkOptionMenu(row_frame, values=["AM", "PM"], width=70)
        ampm_menu.set(ampm_str)
        ampm_menu.pack(side="left", padx=2)
        
        del_btn = ctk.CTkButton(row_frame, text="X", width=30, fg_color="red", 
                                command=lambda: self._delete_video_ui(row_frame, path))
        del_btn.pack(side="right", padx=5)
        
        # Store ref to get data later
        row_frame.data = {
            "path_obj": path,
            "d_ent": d_ent,
            "t_ent": t_ent,
            "ampm_menu": ampm_menu
        }
        self.video_rows.append(row_frame)

    def _delete_video_ui(self, frame, path):
        if frame in self.video_rows:
            self.video_rows.remove(frame)
        frame.destroy()
        if self.on_delete_video:
            self.on_delete_video(path)

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

    def display_history(self, history):
        # For now, maybe just log to console or a popup, or a tab?
        # Simplify: print to log
        if not history:
            return
        last = history[-1]
        self.log(f"History updated: last {last.get('status')} at {last.get('time_str')}")

    def update_status(self, msg):
        self.status_bar.configure(text=msg)

    def log(self, msg):
        print(f"[LOG] {msg}")
        self.status_bar.configure(text=f"Last Log: {msg}")

    def show_message(self, title, msg):
        messagebox.showinfo(title, msg)

    def set_processing_state(self, is_processing):
        state = "disabled" if is_processing else "normal"
        self.start_btn.configure(state=state)
        self.import_btn.configure(state=state)

