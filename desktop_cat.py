import tkinter as tk
import random
import os
import sys
import ctypes
from PIL import Image, ImageTk

class DesktopCat:
    def __init__(self):
        # 1. メインウィンドウの設定
        self.root = tk.Tk()
        self.root.title("Desktop Cat")
        
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        # WindowsのTkinterで最も安定して背景を透過できる「純白」を透過対象に指定
        self.trans_color = "#ffffff"
        self.root.config(bg=self.trans_color)
        self.root.attributes("-transparentcolor", self.trans_color)

        # パスの解決
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        left1_path = os.path.join(base_path, "cat_left1.png")
        left2_path = os.path.join(base_path, "cat_left2.png")
        right1_path = os.path.join(base_path, "cat_right1.png")
        right2_path = os.path.join(base_path, "cat_right2.png")
        sleep_path = os.path.join(base_path, "cat_sleep.png")

        # 2. 画像の読み込みと【改良版】透過・輪郭クリーン処理
        self.img_left1 = self.load_and_clean_edges(left1_path)
        self.img_left2 = self.load_and_clean_edges(left2_path)
        self.img_right1 = self.load_and_clean_edges(right1_path)
        self.img_right2 = self.load_and_clean_edges(right2_path)
        self.img_sleep = self.load_and_clean_edges(sleep_path)
        
        # 3. キャラクターを表示するラベルの設定
        self.label = tk.Label(self.root, image=self.img_left1, bg=self.trans_color, bd=0)
        self.label.pack()

        # 4. 初期位置とステータスの変数
        self.x = 500
        self.y = 500
        self.dx = 0
        self.dy = 0
        self.move_counter = 0
        self.is_tracking = False  
        
        # 放置判定用の変数
        self.last_mouse_x = self.root.winfo_pointerx()
        self.last_mouse_y = self.root.winfo_pointery()
        self.idle_counter = 0     
        self.is_sleeping = False  

        # アニメーション制御用の変数
        self.anim_frame = 0       
        self.anim_counter = 0     
        self.facing_right = False 

        # マルチディスプレイ（2画面）対応の画面サイズ取得
        user32 = ctypes.windll.user32
        self.screen_left = user32.GetSystemMetrics(76)   
        self.screen_top = user32.GetSystemMetrics(77)    
        self.screen_width = user32.GetSystemMetrics(78)  
        self.screen_height = user32.GetSystemMetrics(79) 

        # 5. マウスイベントのバインド
        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.drag)
        self.label.bind("<Button-3>", self.exit_app)
        
        self.label.bind("<Enter>", self.wake_up)
        self.root.bind_all("<Key>", self.reset_idle_by_key)

        self.update_behavior()
        self.root.mainloop()

    # --- 【ここを修正】半透明なフチの白残りをカットする関数 ---
    def load_and_clean_edges(self, path):
        """画像の半透明なフチ（アンチエイリアス）を検知し、完全に除去してドットをくっきりさせる関数"""
        # ドット絵の質感を保つために NEAREST でリサイズ
        img = Image.open(path).convert("RGBA").resize((64, 64), Image.Resampling.NEAREST)
        datas = img.getdata()
        
        new_data = []
        for item in datas:
            r, g, b, a = item
            
            # 1. もともと「ほぼ透明」な背景や半透明なフチ（アルファ値が180未満）は、
            #    Tkinterが透過キーとして認識できるように「純粋な白（255, 255, 255）」に強制変換
            if a < 180:
                new_data.append((255, 255, 255, 255))
            else:
                # 2. しっかり不透明な猫の本体は、アルファ値を完全に最大（255）にして
                #    中途半端な透け感をなくし、くっきりしたドット絵にします
                new_data.append((r, g, b, 255))
                
        img.putdata(new_data)
        return ImageTk.PhotoImage(img)
    # ---------------------------------------------------------

    def start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y
        self.wake_up(None)

    def drag(self, event):
        self.x = self.root.winfo_x() + (event.x - self.drag_x)
        self.y = self.root.winfo_y() + (event.y - self.drag_y)
        self.root.geometry(f"+{self.x}+{self.y}")

    def wake_up(self, event):
        if self.is_sleeping:
            self.is_sleeping = False
            self.idle_counter = 0
            self.label.config(image=self.img_left1)
            self.facing_right = False

    def reset_idle_by_key(self, event):
        self.idle_counter = 0
        if self.is_sleeping:
            self.wake_up(None)

    def check_idle_status(self):
        current_mouse_x = self.root.winfo_pointerx()
        current_mouse_y = self.root.winfo_pointery()

        if current_mouse_x == self.last_mouse_x and current_mouse_y == self.last_mouse_y:
            self.idle_counter += 1
        else:
            self.idle_counter = 0
            if self.is_sleeping:
                self.wake_up(None)

        self.last_mouse_x = current_mouse_x
        self.last_mouse_y = current_mouse_y

    def update_behavior(self):
        self.check_idle_status()

        if self.idle_counter >= 300:  
            self.is_sleeping = True

        if self.is_sleeping:
            self.label.config(image=self.img_sleep)
            self.dx = 0
            self.dy = 0
            self.root.after(100, self.update_behavior)
            return

        if self.move_counter <= 0 and not self.is_tracking:
            if random.random() < 0.20:
                self.is_tracking = True
            else:
                self.is_tracking = False
                self.dx = random.choice([-2, -1, 0, 1, 2])
                self.dy = random.choice([-1, 0, 1])
                self.move_counter = random.randint(10, 50)

        if self.is_tracking:
            mouse_x = self.root.winfo_pointerx()
            mouse_y = self.root.winfo_pointery()
            
            target_x = mouse_x - 32
            target_y = mouse_y - 32
            
            if self.x < target_x - 5:
                self.dx = 3  
            elif self.x > target_x + 5:
                self.dx = -3
            else:
                self.dx = 0

            if self.y < target_y - 5:
                self.dy = 2
            elif self.y > target_y + 5:
                self.dy = -2
            else:
                self.dy = 0
                
            if self.dx == 0 and self.dy == 0:
                self.is_tracking = False
                self.move_counter = 0  

        if self.dx < 0:
            self.facing_right = False
        elif self.dx > 0:
            self.facing_right = True

        if self.dx != 0 or self.dy != 0:
            self.anim_counter += 1
            if self.anim_counter >= 3:  
                self.anim_frame = 1 - self.anim_frame
                self.anim_counter = 0
        else:
            self.anim_frame = 0  

        if self.facing_right:
            if self.anim_frame == 0:
                self.label.config(image=self.img_right1)
            else:
                self.label.config(image=self.img_right2)
        else:
            if self.anim_frame == 0:
                self.label.config(image=self.img_left1)
            else:
                self.label.config(image=self.img_left2)

        self.x += self.dx
        self.y += self.dy
        
        if not self.is_tracking and self.move_counter > 0:
            self.move_counter -= 1

        max_x = self.screen_left + self.screen_width - 64
        max_y = self.screen_top + self.screen_height - 64
        self.x = max(self.screen_left, min(self.x, max_x))
        self.y = max(self.screen_top, min(self.y, max_y))

        self.root.geometry(f"+{self.x}+{self.y}")
        self.root.after(100, self.update_behavior)

    def exit_app(self, event):
        self.root.destroy()

if __name__ == "__main__":
    DesktopCat()