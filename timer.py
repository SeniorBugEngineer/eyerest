import tkinter as tk
from tkinter import messagebox

class BorderlessTimer:
    def __init__(self, root):
        self.root = root
        
        # 1. 隱藏原生標題列 (無邊框視窗)
        self.root.overrideredirect(True)
        
        # 2. 永遠置頂 (Always on Top)
        self.root.attributes('-topmost', True)
        
        # 視窗外觀與位置設定 (預設在螢幕中下方)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coord = (screen_width / 2) - (270 / 2)
        y_coord = screen_height - 250
        self.root.geometry(f"270x160+{int(x_coord)}+{int(y_coord)}")
        self.root.configure(bg="#1e1e2e")

        # --- 時間設定（工作 60 分鐘、休息 5 分鐘）---
        self.WORK_TIME = 60 * 60  # 60 分鐘
        self.BREAK_TIME = 5 * 60   # 5 分鐘
        
        self.time_left = self.WORK_TIME
        self.is_working = True
        self.is_running = False
        self.timer_id = None

        # --- 主視窗滑鼠拖移綁定 ---
        self._offsetx = 0
        self._offsety = 0
        self.root.bind("<Button-1>", self.click_window)
        self.root.bind("<B1-Motion>", self.drag_window)

        # --- 右鍵選單 ---
        self.context_menu = tk.Menu(self.root, tearoff=0, bg="#313244", fg="#cdd6f4", activebackground="#45475a")
        self.context_menu.add_command(label="🙈 隱藏視窗", command=self.hide_window)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ 關閉程式", command=self.root.destroy)
        self.root.bind("<Button-3>", self.show_context_menu)
        self.root.bind("<Button-2>", self.show_context_menu)

        # --- 介面元件 ---
        self.label_status = tk.Label(
            root, text="👨‍💻 專注工作中 (右鍵選單)", font=("Microsoft JhengHei", 9),
            fg="#a6adc8", bg="#1e1e2e"
        )
        self.label_status.pack(pady=(12, 2))

        self.label_timer = tk.Label(
            root, text="60:00", font=("Consolas", 32, "bold"),
            fg="#f38ba8", bg="#1e1e2e"
        )
        self.label_timer.pack(pady=2)

        # --- 底部三個控制按鈕列 ---
        frame_btn = tk.Frame(root, bg="#1e1e2e")
        frame_btn.pack(pady=8)

        # 1. 開始/暫停按鈕
        self.btn_start = tk.Button(
            frame_btn, text="▶ 開始", font=("Microsoft JhengHei", 9),
            command=self.toggle_timer, width=6, bg="#89b4fa", fg="#11111b", relief="flat"
        )
        self.btn_start.pack(side=tk.LEFT, padx=3)

        # 2. 重置時間按鈕
        self.btn_reset = tk.Button(
            frame_btn, text="🔄 重置", font=("Microsoft JhengHei", 9),
            command=self.reset_timer, width=6, bg="#313244", fg="#cdd6f4", relief="flat"
        )
        self.btn_reset.pack(side=tk.LEFT, padx=3)

        # 3. 關閉按鈕
        self.btn_close = tk.Button(
            frame_btn, text="✕ 關閉", font=("Microsoft JhengHei", 9),
            command=self.root.destroy, width=6, bg="#f38ba8", fg="#11111b", relief="flat"
        )
        self.btn_close.pack(side=tk.LEFT, padx=3)

        # --- 隱藏狀態下的「迷你還原小圖示」---
        self.mini_window = None
        self.is_dragging_mini = False  # 用於判斷是否正在拖移

        # 🎯【預設開機/啟動時直接以小圖示啟動】
        self.hide_window()

    # --- 隱藏與還原邏輯 ---
    def hide_window(self):
        if self.mini_window is not None:
            return  # 如果已經是小圖示狀態，不重複建立
            
        self.root.withdraw()  # 隱藏主視窗
        
        # 建立迷你還原圖示 (預設在螢幕右下角)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        mini_x = screen_width - 50
        mini_y = screen_height - 100
        
        self.mini_window = tk.Toplevel()
        self.mini_window.overrideredirect(True)
        self.mini_window.attributes('-topmost', True)
        self.mini_window.geometry(f"30x30+{mini_x}+{mini_y}")
        self.mini_window.configure(bg="#89b4fa")
        
        btn_restore = tk.Label(
            self.mini_window, text="⏰", font=("Arial", 12),
            bg="#89b4fa", fg="#11111b", cursor="hand2"
        )
        btn_restore.pack(fill=tk.BOTH, expand=True)

        # 綁定按下滑鼠、拖曳、放開事件
        btn_restore.bind("<Button-1>", self.click_mini_window)
        btn_restore.bind("<B1-Motion>", self.drag_mini_window)
        btn_restore.bind("<ButtonRelease-1>", self.release_mini_window)

    def restore_window(self):
        if self.mini_window:
            self.mini_window.destroy()
            self.mini_window = None
        self.root.deiconify()  # 重新顯示主視窗

    # --- 滑鼠拖移實作 (主視窗) ---
    def click_window(self, event):
        self._offsetx = event.x
        self._offsety = event.y

    def drag_window(self, event):
        x = self.root.winfo_pointerx() - self._offsetx
        y = self.root.winfo_pointery() - self._offsety
        self.root.geometry(f"+{x}+{y}")

    # --- 滑鼠拖移與點擊分離實作 (迷你小圖示) ---
    def click_mini_window(self, event):
        self._offsetx_mini = event.x
        self._offsety_mini = event.y
        self.is_dragging_mini = False  # 重置拖移旗標

    def drag_mini_window(self, event):
        self.is_dragging_mini = True  # 觸發了移動，標記為拖移中
        if self.mini_window:
            x = self.mini_window.winfo_pointerx() - self._offsetx_mini
            y = self.mini_window.winfo_pointery() - self._offsety_mini
            self.mini_window.geometry(f"+{x}+{y}")

    def release_mini_window(self, event):
        # 只有在「沒有移動（單純點擊）」的情況下，放開滑鼠才會還原視窗
        if not self.is_dragging_mini:
            self.restore_window()

    # --- 右鍵選單 ---
    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    # --- 計時邏輯 ---
    def update_timer(self):
        if self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            self.label_timer.config(text=f"{mins:02d}:{secs:02d}")
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            # 如果處於隱藏狀態，時間到自動彈回主視窗
            if self.mini_window:
                self.restore_window()

            if self.is_working:
                self.is_working = False
                self.time_left = self.BREAK_TIME
                self.label_status.config(text="☕ 休息時間", fg="#a6e3a1")
                self.label_timer.config(text="05:00", fg="#a6e3a1")
                messagebox.showinfo("⏰ 休息時間！", "已經連續工作 60 分鐘囉！\n快站起來喝杯水、走動放鬆一下吧！", parent=self.root)
            else:
                self.is_working = True
                self.time_left = self.WORK_TIME
                self.label_status.config(text="👨‍💻 專注工作中", fg="#a6adc8")
                self.label_timer.config(text="60:00", fg="#f38ba8")
                messagebox.showinfo("💪 休息結束！", "5 分鐘休息結束，準備好回到工作狀態了嗎？", parent=self.root)
            
            self.is_running = False
            self.btn_start.config(text="▶ 開始", bg="#89b4fa")

    def toggle_timer(self):
        if self.is_running:
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
            self.is_running = False
            self.btn_start.config(text="▶ 繼續", bg="#89b4fa")
        else:
            self.is_running = True
            self.btn_start.config(text="⏸️ 暫停", bg="#f9e2af")
            self.update_timer()

    def reset_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.is_running = False
        self.is_working = True
        self.time_left = self.WORK_TIME
        self.label_status.config(text="👨‍💻 專注工作中", fg="#a6adc8")
        self.label_timer.config(text="60:00", fg="#f38ba8")
        self.btn_start.config(text="▶ 開始", bg="#89b4fa")

if __name__ == "__main__":
    root = tk.Tk()
    app = BorderlessTimer(root)
    root.mainloop()