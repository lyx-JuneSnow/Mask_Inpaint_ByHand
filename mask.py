import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np

class ImageMaskerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Masking Tool")
        
        # 图像文件路径
        self.image_path = None
        self.image = None
        self.mask = None
        self.canvas = None
        self.drawing = False
        self.brush_width = 5  # 默认涂抹宽度

        # 创建选择图片按钮
        self.load_button = tk.Button(self.root, text="选择图片", command=self.load_image)
        self.load_button.pack()

        # 创建保存掩码按钮
        self.save_button = tk.Button(self.root, text="保存掩码", command=self.save_mask, state=tk.DISABLED)
        self.save_button.pack()

        # 创建调整涂抹宽度的输入框
        self.brush_label = tk.Label(self.root, text="涂抹宽度:")
        self.brush_label.pack()
        self.brush_width_entry = tk.Entry(self.root)
        self.brush_width_entry.insert(0, str(self.brush_width))
        self.brush_width_entry.pack()

        # 创建确认按钮，调整涂抹宽度
        self.brush_width_button = tk.Button(self.root, text="确认", command=self.update_brush_width)
        self.brush_width_button.pack()

    def load_image(self):
        # 选择图片文件
        self.image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.bmp")])
        if not self.image_path:
            return
        
        # 加载原始图像
        self.image = Image.open(self.image_path)
        self.original_width, self.original_height = self.image.size

        # 计算新的宽度，保持宽高比
        new_height = 600
        new_width = int(self.original_width * (new_height / self.original_height))
        self.image = self.image.resize((new_width, new_height))  # 缩放图片

        self.tk_image = ImageTk.PhotoImage(self.image)

        # 清空之前的涂抹内容
        if self.canvas:
            self.canvas.destroy()
        
        # 创建新的Canvas
        self.canvas = tk.Canvas(self.root, width=self.tk_image.width(), height=self.tk_image.height())
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        
        # 创建一个与原图一致大小的掩码
        self.mask = np.zeros((self.original_height, self.original_width), dtype=np.uint8)  # 掩码尺寸与原图一致
        
        # 绑定鼠标事件
        self.canvas.bind("<ButtonPress-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

        self.save_button.config(state=tk.NORMAL)

    def start_drawing(self, event):
        self.drawing = True
        self.last_x, self.last_y = event.x, event.y

    def draw(self, event):
        if self.drawing:
            x, y = event.x, event.y
            self.canvas.create_line(self.last_x, self.last_y, x, y, width=self.brush_width, fill="red", capstyle=tk.ROUND, smooth=tk.TRUE)
            
            # 更新掩码，涂抹区域标记为1
            self.update_mask(self.last_x, self.last_y, x, y)
            
            self.last_x, self.last_y = x, y

    def stop_drawing(self, event):
        self.drawing = False

    def update_mask(self, x1, y1, x2, y2):
        # 计算涂抹区域的矩形范围
        brush_half = self.brush_width // 2
        x_start, x_end = min(x1, x2) - brush_half, max(x1, x2) + brush_half
        y_start, y_end = min(y1, y2) - brush_half, max(y1, y2) + brush_half

        # 将涂抹区域的坐标从显示图像转换为原图的坐标系
        scale_x = self.original_width / self.image.width
        scale_y = self.original_height / self.image.height
        x_start = int(x_start * scale_x)
        x_end = int(x_end * scale_x)
        y_start = int(y_start * scale_y)
        y_end = int(y_end * scale_y)

        # 更新掩码：涂抹区域标记为1，确保不会超出掩码范围
        for x in range(x_start, x_end):
            for y in range(y_start, y_end):
                if 0 <= x < self.mask.shape[1] and 0 <= y < self.mask.shape[0]:
                    self.mask[y, x] = 1

    def save_mask(self):
        # 将掩码保存为图像文件
        mask_image = Image.fromarray(self.mask * 255)  # 二进制掩码图像
        mask_image = mask_image.resize((self.original_width, self.original_height))  # 将掩码图像调整为与原图一致
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if save_path:
            mask_image.save(save_path)
            print(f"掩码保存成功：{save_path}")

    def update_brush_width(self):
        try:
            # 获取用户输入的涂抹宽度，并更新
            self.brush_width = int(self.brush_width_entry.get())
        except ValueError:
            print("请输入有效的涂抹宽度")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageMaskerApp(root)
    root.mainloop()
