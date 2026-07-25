import sys
import tkinter as tk
from tkinter import messagebox

# 嘗試載入 Windows API 模組以監聽鎖定與睡眠事件
WIN32_AVAILABLE = False
if sys.platform == "win32":
    try:
        import win32gui
        import win32con
        import win32ts
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False

# 手動補充 win32con / win32ts 缺少的 Windows 常數
WM_WTSSESSION_CHANGE = 0x02B1
WTS_SESSION_LOCK = 0x7
WTS_SESSION_UNLOCK = 0x8
WTS_SESSION_LOGON = 0x5
WTS_SESSION_LOGOFF = 0x6


class BorderlessTimer:
    def __init__(self, root):
        self.root = root

        # 1. 隱藏原生標題列 (無邊框視窗)
        self.root.overrideredirect(True)

        # 2. 永遠置頂 (Always on Top)
        self.root.attributes('-topmost', True)

        # 3. 預設透明度設定 (1.0 = 不透明, 0.1 ~ 1.0)
        self.alpha_var = tk.DoubleVar(value=0.9)
        self.root.attributes('-alpha', self.alpha_var.get())

        # 視窗外觀與位置設定 (寬 300、高 190)
        self.WIN_WIDTH = 300
        self.WIN_HEIGHT = 190
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coord = (screen_width / 2) - (self.WIN_WIDTH / 2)
        y_coord = screen_height - 250
        self.root.geometry(f"{self.WIN_WIDTH}x{self.WIN_HEIGHT}+{int(x_coord)}+{int(y_coord)}")

        # --- 時間設定（工作 60 分鐘、休息 5 分鐘）---
        self.WORK_TIME = 60 * 60  # 60 分鐘
        self.BREAK_TIME = 5 * 60   # 5 分鐘

        self.time_left = self.WORK_TIME
        self.is_working = True
        self.is_running = False
        self.timer_id = None

        # 智慧自動暫停標記
        self.auto_paused_by_system = False

        # 閃爍提醒變數
        self.flash_id = None
        self.is_flashing = False
        self.flash_state = False

        # ✨ 動畫相關變數
        self.zoom_anim_id = None
        self.BASE_FONT_SIZE = 34
        self.MAX_FONT_SIZE = 48
        
        # 迷你圖示動畫字體與尺寸設定
        self.MINI_BASE_FONT_SIZE = 11
        self.MINI_MAX_FONT_SIZE = 15  # 放大字體

        # --- 🎨 主題配色設定 ---
        self.themes = {
            "catppuccin": {
                "name": "🌌 藍紫極光 (Catppuccin)",
                "bg": "#1e1e2e",
                "fg_status": "#a6adc8",
                "timer_work": "#f38ba8",
                "timer_break": "#a6e3a1",
                "btn_start_bg": "#89b4fa",
                "btn_start_fg": "#11111b",
                "btn_other_bg": "#313244",
                "btn_other_fg": "#cdd6f4",
                "btn_close_bg": "#f38ba8",
                "btn_close_fg": "#11111b",
                "mini_bg": "#89b4fa",
                "mini_fg": "#11111b",
                "resume_bg": "#a6e3a1",
                "resume_fg": "#11111b"
            },
            "dark_gold": {
                "name": "🖤 經典暗黑 (Dark Gold)",
                "bg": "#121212",
                "fg_status": "#abb2bf",
                "timer_work": "#e5c07b",
                "timer_break": "#98c379",
                "btn_start_bg": "#d19a66",
                "btn_start_fg": "#121212",
                "btn_other_bg": "#21252b",
                "btn_other_fg": "#abb2bf",
                "btn_close_bg": "#e06c75",
                "btn_close_fg": "#121212",
                "mini_bg": "#e5c07b",
                "mini_fg": "#121212",
                "resume_bg": "#98c379",
                "resume_fg": "#121212"
            },
            "pastel_pink": {
                "name": "🌸 櫻花粉紅 (Pastel Pink)",
                "bg": "#fff0f3",
                "fg_status": "#590d22",
                "timer_work": "#ff4d6d",
                "timer_break": "#38b000",
                "btn_start_bg": "#ffb3c1",
                "btn_start_fg": "#590d22",
                "btn_other_bg": "#ffccd5",
                "btn_other_fg": "#590d22",
                "btn_close_bg": "#c9184a",
                "btn_close_fg": "#ffffff",
                "mini_bg": "#ffb3c1",
                "mini_fg": "#590d22",
                "resume_bg": "#80ed99",
                "resume_fg": "#004b23"
            }
        }
        self.selected_theme_var = tk.StringVar(value="catppuccin")
        self.current_theme = self.themes[self.selected_theme_var.get()]

        # --- 主視窗滑鼠拖移與邊界限制綁定 ---
        self._offsetx = 0
        self._offsety = 0
        self.root.bind("<Button-1>", self.click_window)
        self.root.bind("<B1-Motion>", self.drag_window)
        self.root.bind("<ButtonRelease-1>", self.release_window)

        # --- 右鍵選單 ---
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.setup_theme_menu(self.context_menu)
        self.setup_alpha_menu(self.context_menu)
        self.context_menu.add_command(label="🧪 測試最後 10 秒動畫", command=self.test_countdown_anim)
        self.context_menu.add_command(label="🙈 隱藏視窗", command=self.hide_window)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ 關閉程式", command=self.root.destroy)

        self.root.bind("<Button-3>", self.show_context_menu)
        self.root.bind("<Button-2>", self.show_context_menu)

        # --- 頂部標題與按鈕列 ---
        self.frame_top = tk.Frame(root)
        self.frame_top.pack(fill=tk.X, padx=12, pady=(10, 0))

        self.label_status = tk.Label(
            self.frame_top, text="👨‍💻 專注工作中", font=("Microsoft JhengHei", 9), anchor="w"
        )
        self.label_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.btn_hide = tk.Button(
            self.frame_top, text="➖ 隱藏", font=("Microsoft JhengHei", 8),
            command=self.hide_window, relief="flat", padx=5, pady=1, cursor="hand2"
        )
        self.btn_hide.pack(side=tk.RIGHT, padx=(3, 0))

        self.btn_alpha = tk.Button(
            self.frame_top, text="💧 透明", font=("Microsoft JhengHei", 8),
            command=self.show_alpha_popup_menu, relief="flat", padx=5, pady=1, cursor="hand2"
        )
        self.btn_alpha.pack(side=tk.RIGHT, padx=(3, 0))

        self.btn_theme = tk.Button(
            self.frame_top, text="🎨 主題", font=("Microsoft JhengHei", 8),
            command=self.show_theme_popup_menu, relief="flat", padx=5, pady=1, cursor="hand2"
        )
        self.btn_theme.pack(side=tk.RIGHT, padx=(3, 0))

        self.popup_theme_menu = tk.Menu(self.root, tearoff=0)
        self.build_theme_radio_menu(self.popup_theme_menu)

        self.popup_alpha_menu = tk.Menu(self.root, tearoff=0)
        self.build_alpha_radio_menu(self.popup_alpha_menu)

        # --- 倒數計時顯示 ---
        self.label_timer = tk.Label(
            root, text="60:00", font=("Consolas", self.BASE_FONT_SIZE, "bold")
        )
        self.label_timer.pack(pady=(4, 0))

        # --- 🟢 提示區域 ---
        self.frame_notice = tk.Frame(root, height=24)
        self.frame_notice.pack(fill=tk.X, pady=(1, 1))
        self.frame_notice.pack_propagate(False)

        self.frame_notice_inner = tk.Frame(self.frame_notice)
        
        self.label_notice = tk.Label(
            self.frame_notice_inner, text="▶ 已解鎖：自動恢復倒數",
            font=("Microsoft JhengHei", 8, "bold")
        )
        self.label_notice.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_close_notice = tk.Button(
            self.frame_notice_inner, text="✕", font=("Microsoft JhengHei", 7, "bold"),
            command=self.clear_resume_notice, relief="flat", bd=0, padx=3, pady=0, cursor="hand2"
        )
        self.btn_close_notice.pack(side=tk.LEFT)

        # --- 底部三個控制按鈕列 ---
        self.frame_btn = tk.Frame(root)
        self.frame_btn.pack(pady=6)

        self.btn_start = tk.Button(
            self.frame_btn, text="▶ 開始", font=("Microsoft JhengHei", 9),
            command=self.toggle_timer, width=7, relief="flat", cursor="hand2"
        )
        self.btn_start.pack(side=tk.LEFT, padx=4)

        self.btn_reset = tk.Button(
            self.frame_btn, text="🔄 重置", font=("Microsoft JhengHei", 9),
            command=self.reset_timer, width=7, relief="flat", cursor="hand2"
        )
        self.btn_reset.pack(side=tk.LEFT, padx=4)

        self.btn_close = tk.Button(
            self.frame_btn, text="✕ 關閉", font=("Microsoft JhengHei", 9),
            command=self.root.destroy, width=7, relief="flat", cursor="hand2"
        )
        self.btn_close.pack(side=tk.LEFT, padx=4)

        # 迷你懸浮視窗變數
        self.mini_window = None
        self.btn_restore = None
        self.is_dragging_mini = False

        self.apply_theme()
        self.setup_system_event_listener()
        
        # 啟動時直接進入小圖示懸浮模式
        self.hide_window()

    # --- 🎬 數字放大與迷你視窗脈衝動畫 ---
    def trigger_zoom_animation(self):
        if self.zoom_anim_id:
            self.root.after_cancel(self.zoom_anim_id)

        steps = 6
        delay = 30  # ms

        main_inc = (self.MAX_FONT_SIZE - self.BASE_FONT_SIZE) / steps
        mini_inc = (self.MINI_MAX_FONT_SIZE - self.MINI_BASE_FONT_SIZE) / steps

        # 主題預設背景色與警示顏色
        t = self.current_theme
        normal_bg = t["mini_bg"]
        alert_bg = "#f38ba8"  # 倒數脈衝時的亮紅色背景

        def animate(step=0, growing=True):
            if step > steps:
                growing = False
                step = steps

            if not growing and step <= 0:
                self.reset_timer_font()
                return

            # 主視窗放大
            current_main_size = int(self.BASE_FONT_SIZE + step * main_inc)
            self.label_timer.config(font=("Consolas", current_main_size, "bold"))

            # 迷你視窗處理（動態放大視窗尺寸 + 背景色脈衝）
            if self.mini_window and self.btn_restore and self.is_running:
                current_mini_size = int(self.MINI_BASE_FONT_SIZE + step * mini_inc)
                self.btn_restore.config(font=("Consolas", current_mini_size, "bold"))

                # 依動態步驟動態微調迷你視窗寬度與高度 (讓大字體不被切到)
                cur_x = self.mini_window.winfo_x()
                cur_y = self.mini_window.winfo_y()
                mini_w = int(65 + step * 2.5)  # 從 65 變大至 80
                mini_h = int(28 + step * 0.8)  # 從 28 變大至 32
                self.mini_window.geometry(f"{mini_w}x{mini_h}+{cur_x}+{cur_y}")

                # 背景色脈衝 (靠近最大步驟時變警示色)
                bg_col = alert_bg if step >= 3 else normal_bg
                fg_col = "#11111b" if step >= 3 else t["mini_fg"]
                self.mini_window.configure(bg=bg_col)
                self.btn_restore.configure(bg=bg_col, fg=fg_col)

            next_step = step + 1 if growing else step - 1
            self.zoom_anim_id = self.root.after(delay, animate, next_step, growing)

        animate(0, True)

    def reset_timer_font(self):
        if self.zoom_anim_id:
            self.root.after_cancel(self.zoom_anim_id)
            self.zoom_anim_id = None
            
        self.label_timer.config(font=("Consolas", self.BASE_FONT_SIZE, "bold"))
        
        if self.mini_window and self.btn_restore and self.is_running:
            t = self.current_theme
            self.mini_window.configure(bg=t["mini_bg"])
            self.btn_restore.configure(
                bg=t["mini_bg"], 
                fg=t["mini_fg"], 
                font=("Consolas", self.MINI_BASE_FONT_SIZE, "bold")
            )
            # 復原預設迷你尺寸
            cur_x = self.mini_window.winfo_x()
            cur_y = self.mini_window.winfo_y()
            self.mini_window.geometry(f"65x28+{cur_x}+{cur_y}")

    # --- 🧪 測試用：直接跳到最後 10 秒看動畫 ---
    def test_countdown_anim(self):
        self.reset_timer()
        self.time_left = 10
        self.toggle_timer()

    # --- 💧 透明度選單與控制邏輯 ---
    def build_alpha_radio_menu(self, target_menu):
        options = [
            ("100% (完全不透明)", 1.0),
            ("90% (推薦)", 0.9),
            ("80%", 0.8),
            ("60%", 0.6),
            ("40% (高度半透明)", 0.4),
        ]
        for label, val in options:
            target_menu.add_radiobutton(
                label=label,
                variable=self.alpha_var,
                value=val,
                command=self.on_alpha_change
            )

    def setup_alpha_menu(self, parent_menu):
        self.sub_alpha_menu = tk.Menu(parent_menu, tearoff=0)
        self.build_alpha_radio_menu(self.sub_alpha_menu)
        parent_menu.add_cascade(label="💧 調整透明度", menu=self.sub_alpha_menu)

    def show_alpha_popup_menu(self):
        x = self.btn_alpha.winfo_rootx()
        y = self.btn_alpha.winfo_rooty() + self.btn_alpha.winfo_height()
        self.popup_alpha_menu.post(x, y)

    def on_alpha_change(self):
        val = self.alpha_var.get()
        self.root.attributes('-alpha', val)
        if self.mini_window:
            self.mini_window.attributes('-alpha', val)

    # --- 🛡️ 螢幕邊界檢查邏輯 ---
    def clamp_to_screen(self, window, x, y, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        clamped_x = max(0, min(x, screen_width - width))
        clamped_y = max(0, min(y, screen_height - height))

        return clamped_x, clamped_y

    # --- 滑鼠拖移實作 (主視窗) ---
    def click_window(self, event):
        self._offsetx = event.x
        self._offsety = event.y

    def drag_window(self, event):
        x = self.root.winfo_pointerx() - self._offsetx
        y = self.root.winfo_pointery() - self._offsety
        self.root.geometry(f"+{x}+{y}")

    def release_window(self, event):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        clamped_x, clamped_y = self.clamp_to_screen(
            self.root, x, y, self.WIN_WIDTH, self.WIN_HEIGHT
        )
        self.root.geometry(f"+{clamped_x}+{clamped_y}")

    # --- 滑鼠拖移與點擊分離實作 (迷你小圖示) ---
    def click_mini_window(self, event):
        self._offsetx_mini = event.x
        self._offsety_mini = event.y
        self.is_dragging_mini = False

    def drag_mini_window(self, event):
        self.is_dragging_mini = True
        if self.mini_window:
            x = self.mini_window.winfo_pointerx() - self._offsetx_mini
            y = self.mini_window.winfo_pointery() - self._offsety_mini
            self.mini_window.geometry(f"+{x}+{y}")

    def release_mini_window(self, event):
        if self.is_dragging_mini and self.mini_window:
            x = self.mini_window.winfo_x()
            y = self.mini_window.winfo_y()
            w = self.mini_window.winfo_width()
            h = self.mini_window.winfo_height()

            clamped_x, clamped_y = self.clamp_to_screen(
                self.mini_window, x, y, w, h
            )
            self.mini_window.geometry(f"+{clamped_x}+{clamped_y}")
        else:
            self.restore_window()

    # --- ⏸️ 智慧自動暫停與恢復：Windows 系統事件監聽 ---
    def setup_system_event_listener(self):
        if not WIN32_AVAILABLE:
            return

        hwnd = self.root.winfo_id()

        try:
            win32ts.WTSRegisterSessionNotification(hwnd, win32ts.NOTIFY_FOR_THIS_SESSION)
        except Exception:
            pass

        self.old_wndproc = win32gui.SetWindowLong(hwnd, win32con.GWL_WNDPROC, self.wnd_proc)

    def wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == WM_WTSSESSION_CHANGE:
            if wparam in (WTS_SESSION_LOCK, WTS_SESSION_LOGOFF):
                self.on_system_pause()
            elif wparam in (WTS_SESSION_UNLOCK, WTS_SESSION_LOGON):
                self.on_system_resume()

        elif msg == win32con.WM_POWERBROADCAST:
            if wparam in (win32con.PBT_APMSUSPEND, win32con.PBT_APMSTANDBY):
                self.on_system_pause()
            elif wparam in (win32con.PBT_APMRESUMEAUTOMATIC, win32con.PBT_APMRESUMESUSPEND):
                self.on_system_resume()

        return win32gui.CallWindowProc(self.old_wndproc, hwnd, msg, wparam, lparam)

    def on_system_pause(self):
        if self.is_running:
            self.auto_paused_by_system = True
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
            self.is_running = False
            self.btn_start.config(text="▶ 繼續")
            self.label_status.config(text="⏸️ 已暫停 (電腦鎖定)")
            self.reset_timer_font()
            self.update_mini_display()

    def on_system_resume(self):
        if self.auto_paused_by_system:
            self.auto_paused_by_system = False

            if self.mini_window:
                self.restore_window()
            else:
                self.root.deiconify()
                self.root.lift()
                self.root.attributes('-topmost', True)

            self.is_running = True
            self.btn_start.config(text="⏸️ 暫停")

            t = self.current_theme
            resume_bg = t["resume_bg"]
            resume_fg = t["resume_fg"]

            self.frame_notice_inner.configure(bg=resume_bg)
            self.label_notice.config(bg=resume_bg, fg=resume_fg)
            self.btn_close_notice.config(bg=resume_fg, fg=resume_bg)
            
            self.frame_notice_inner.pack(expand=True)

            self.root.configure(bg=resume_bg)
            self.frame_top.configure(bg=resume_bg)
            self.frame_notice.configure(bg=resume_bg)
            self.frame_btn.configure(bg=resume_bg)

            self.label_status.configure(bg=resume_bg, fg=resume_fg)
            self.label_timer.configure(bg=resume_bg, fg=resume_fg)

            status_text = "👨‍💻 專注工作中" if self.is_working else "☕ 休息時間"
            self.label_status.config(text=status_text)

            self.root.update_idletasks()
            self.update_timer()

    def clear_resume_notice(self):
        self.frame_notice_inner.pack_forget()
        self.apply_theme()

    # --- 🎨 主題選單與套用 ---
    def build_theme_radio_menu(self, target_menu):
        for key, info in self.themes.items():
            target_menu.add_radiobutton(
                label=info["name"],
                variable=self.selected_theme_var,
                value=key,
                command=self.on_theme_select
            )

    def setup_theme_menu(self, parent_menu):
        self.sub_theme_menu = tk.Menu(parent_menu, tearoff=0)
        self.build_theme_radio_menu(self.sub_theme_menu)
        parent_menu.add_cascade(label="🎨 切換主題", menu=self.sub_theme_menu)

    def show_theme_popup_menu(self):
        x = self.btn_theme.winfo_rootx()
        y = self.btn_theme.winfo_rooty() + self.btn_theme.winfo_height()
        self.popup_theme_menu.post(x, y)

    def on_theme_select(self):
        key = self.selected_theme_var.get()
        if key in self.themes:
            self.current_theme = self.themes[key]
            self.apply_theme()

    def apply_theme(self):
        t = self.current_theme

        self.root.configure(bg=t["bg"])
        self.frame_top.configure(bg=t["bg"])
        self.frame_notice.configure(bg=t["bg"])
        self.frame_btn.configure(bg=t["bg"])

        self.label_status.configure(bg=t["bg"], fg=t["fg_status"])
        timer_fg = t["timer_work"] if self.is_working else t["timer_break"]
        self.label_timer.configure(bg=t["bg"], fg=timer_fg)

        self.btn_start.configure(bg=t["btn_start_bg"], fg=t["btn_start_fg"])
        self.btn_reset.configure(bg=t["btn_other_bg"], fg=t["btn_other_fg"])
        self.btn_close.configure(bg=t["btn_close_bg"], fg=t["btn_close_fg"])
        self.btn_hide.configure(bg=t["btn_other_bg"], fg=t["btn_other_fg"])
        self.btn_alpha.configure(bg=t["btn_other_bg"], fg=t["btn_other_fg"])
        self.btn_theme.configure(bg=t["btn_other_bg"], fg=t["btn_other_fg"])

        menu_kwargs = {
            "bg": t["btn_other_bg"],
            "fg": t["btn_other_fg"],
            "activebackground": t["btn_start_bg"],
            "activeforeground": t["btn_start_fg"],
            "selectcolor": t["btn_start_bg"]
        }
        self.context_menu.configure(bg=t["btn_other_bg"], fg=t["btn_other_fg"], activebackground=t["btn_start_bg"], activeforeground=t["btn_start_fg"])
        self.sub_theme_menu.configure(**menu_kwargs)
        self.popup_theme_menu.configure(**menu_kwargs)
        self.sub_alpha_menu.configure(**menu_kwargs)
        self.popup_alpha_menu.configure(**menu_kwargs)

        if self.mini_window and self.btn_restore:
            self.mini_window.configure(bg=t["mini_bg"])
            self.btn_restore.configure(bg=t["mini_bg"], fg=t["mini_fg"])

    # --- 閃爍提醒邏輯 ---
    def start_flashing(self):
        if self.is_flashing:
            return
        self.is_flashing = True
        self.flash_loop()

    def flash_loop(self):
        if not self.is_flashing:
            return

        self.flash_state = not self.flash_state
        bg_color = "#f38ba8" if self.flash_state else "#f9e2af"
        fg_color = "#11111b"

        self.root.configure(bg=bg_color)
        self.frame_top.configure(bg=bg_color)
        self.frame_notice.configure(bg=bg_color)
        self.frame_btn.configure(bg=bg_color)
        self.label_status.configure(bg=bg_color, fg=fg_color)
        self.label_timer.configure(bg=bg_color, fg=fg_color)

        if self.mini_window and self.btn_restore:
            self.mini_window.configure(bg=bg_color)
            self.btn_restore.configure(bg=bg_color, fg=fg_color)

        self.flash_id = self.root.after(500, self.flash_loop)

    def stop_flashing(self):
        self.is_flashing = False
        if self.flash_id:
            self.root.after_cancel(self.flash_id)
            self.flash_id = None
        self.apply_theme()

    # --- 小圖示狀態顯示更新邏輯 ---
    def update_mini_display(self):
        if not self.mini_window or not self.btn_restore:
            return

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        if self.is_running:
            mins, secs = divmod(self.time_left, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            cur_x = self.mini_window.winfo_x()
            cur_y = self.mini_window.winfo_y()
            if cur_x <= 0 and cur_y <= 0:
                cur_x = screen_width - 85
                cur_y = screen_height - 100
            self.mini_window.geometry(f"65x28+{cur_x}+{cur_y}")
            self.btn_restore.config(text=time_str, font=("Consolas", self.MINI_BASE_FONT_SIZE, "bold"))
        else:
            cur_x = self.mini_window.winfo_x()
            cur_y = self.mini_window.winfo_y()
            if cur_x <= 0 and cur_y <= 0:
                cur_x = screen_width - 50
                cur_y = screen_height - 100
            self.mini_window.geometry(f"30x30+{cur_x}+{cur_y}")
            self.btn_restore.config(text="⏰", font=("Arial", 12))

    # --- 隱藏與還原邏輯 ---
    def hide_window(self):
        if self.mini_window is not None:
            return

        self.root.withdraw()

        t = self.current_theme
        self.mini_window = tk.Toplevel()
        self.mini_window.overrideredirect(True)
        self.mini_window.attributes('-topmost', True)
        self.mini_window.attributes('-alpha', self.alpha_var.get())
        self.mini_window.configure(bg=t["mini_bg"])

        self.btn_restore = tk.Label(
            self.mini_window, bg=t["mini_bg"], fg=t["mini_fg"], cursor="hand2"
        )
        self.btn_restore.pack(fill=tk.BOTH, expand=True)

        self.btn_restore.bind("<Button-1>", self.click_mini_window)
        self.btn_restore.bind("<B1-Motion>", self.drag_mini_window)
        self.btn_restore.bind("<ButtonRelease-1>", self.release_mini_window)

        self.update_mini_display()

    def restore_window(self):
        self.stop_flashing()

        if self.mini_window:
            self.mini_window.destroy()
            self.mini_window = None
            self.btn_restore = None
        self.root.deiconify()

    # --- 右鍵選單 ---
    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    # --- 計時邏輯 ---
    def update_timer(self):
        if self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            time_str = f"{mins:02d}:{secs:02d}"

            self.label_timer.config(text=time_str)

            if self.btn_restore and self.is_running:
                self.btn_restore.config(text=time_str)

            # 🎬 當進入最後 10 秒時，觸發放大脈衝與視窗背景閃爍效果
            if self.time_left <= 10:
                self.trigger_zoom_animation()

            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.reset_timer_font()

            if self.mini_window:
                self.restore_window()

            self.start_flashing()

            if self.is_working:
                self.is_working = False
                self.time_left = self.BREAK_TIME
                self.label_status.config(text="☕ 休息時間")
                self.label_timer.config(text="05:00")
                messagebox.showinfo("⏰ 休息時間！", "已經連續工作 60 分鐘囉！\n快站起來喝杯水、走動放鬆一下吧！", parent=self.root)
            else:
                self.is_working = True
                self.time_left = self.WORK_TIME
                self.label_status.config(text="👨‍💻 專注工作中")
                self.label_timer.config(text="60:00")
                messagebox.showinfo("💪 休息結束！", "5 分鐘休息結束，準備好回到工作狀態了嗎？", parent=self.root)

            self.stop_flashing()
            self.is_running = False
            self.btn_start.config(text="▶ 開始")
            self.update_mini_display()

    def toggle_timer(self):
        self.stop_flashing()
        self.auto_paused_by_system = False

        if self.is_running:
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
            self.is_running = False
            self.btn_start.config(text="▶ 繼續")
            self.reset_timer_font()
            self.update_mini_display()
        else:
            self.is_running = True
            self.btn_start.config(text="⏸️ 暫停")
            status_text = "👨‍💻 專注工作中" if self.is_working else "☕ 休息時間"
            self.label_status.config(text=status_text)
            self.update_mini_display()
            self.update_timer()

    def reset_timer(self):
        self.stop_flashing()
        self.reset_timer_font()
        self.auto_paused_by_system = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.is_running = False
        self.is_working = True
        self.time_left = self.WORK_TIME
        self.label_status.config(text="👨‍💻 專注工作中")
        self.label_timer.config(text="60:00")
        self.btn_start.config(text="▶ 開始")
        self.apply_theme()
        self.update_mini_display()


if __name__ == "__main__":
    root = tk.Tk()
    app = BorderlessTimer(root)
    root.mainloop()