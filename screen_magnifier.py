# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
https://github.com/zyprex/pymag
"""

import tkinter as tk
from pyautogui import position
from PIL import Image, ImageTk, ImageGrab, ImageDraw

ratio = 1.3
new_image = None 

class Application(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        self.master.title("pymag - a simple screen magnifier")
        # widget
        self.state_txt = None
        self.state_label = tk.Label(self, text=None)
        self.state_label.pack()
        self.label_img = tk.Label(self, image=None)
        self.label_img.pack()
        # bind event
        self.width = self.master.winfo_width()
        
        # self.mouse_x, self.mouse_y = position()
        self.mouse_x = position()[0] - self.master.winfo_width()/2 / ratio
        self.mouse_y = position()[1] - self.master.winfo_height()/2 / ratio
        
        self.height = self.master.winfo_height()
        self.bind('<Configure>', self.on_resize)
        self.bind_all('<Key>', self.key_pressed)
        # with Windows OS
        self.bind_all('<MouseWheel>', self.mouse_wheel)
        # with Linux OS
        self.bind_all('<Button-4>', self.mouse_wheel)
        self.bind_all('<Button-5>', self.mouse_wheel)
        # main loop 
        self.forever()

    def update_state(self):
        global ratio
        
        #self.mouse_x, self.mouse_y = position()
        self.mouse_x = position()[0] - self.master.winfo_width()/2 / ratio
        self.mouse_y = position()[1] - self.master.winfo_height()/2 / ratio
        
        self.state_txt = 'X{} | x: {}, y: {} |  w: {}, h: {}'.format(ratio,
                self.mouse_x, self.mouse_y, self.width, self.height)
        self.state_label['text'] = self.state_txt

    def on_resize(self, event):
        # print("w: {}, h: {}".format(self.master.winfo_width(),
        # self.master.winfo_height())) 
        self.width = self.master.winfo_width()
        self.height = self.master.winfo_height()
        self.update_state()

    def key_pressed(self, event):
        # hprint(event.char)
        if event.keysym == "Escape":
            root.destroy()

    def mouse_wheel(self, event):
        global ratio
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            ratio -= 0.1
        if event.num == 4 or event.delta == 120:
            ratio += 0.1
        ratio = round(ratio, 2)
        if ratio < 1:
            ratio = 1.0

    def forever(self):
        global new_image, ratio
        self.update_state()
        ss_region = (self.mouse_x, self.mouse_y, self.mouse_x +
                self.width/ratio, self.mouse_y + self.height/ratio) 
        ss_img = ImageGrab.grab(ss_region)
        resized_image = ss_img.resize((round(self.width*ratio),
            round(self.height*ratio)), Image.LANCZOS)
      
        # Draw crosshair
        draw = ImageDraw.Draw(resized_image)
        x_center = resized_image.width // 2
        y_center = resized_image.height // 2
        draw.line((x_center, 0, x_center, resized_image.height), fill='white', width=3)
        draw.line((0, y_center, resized_image.width, y_center), fill='white', width=3)
        
        new_image = ImageTk.PhotoImage(resized_image)
        self.label_img['image'] = new_image
        self.master.after(round(ratio*25), self.forever)

root = tk.Tk()
root.geometry("300x300") # width x height

'''
canvas = tk.Canvas(root, width=300, height=300)
canvas.pack()

# Load the transparent PNG image
image = Image.open("crosshair.png")
photo = ImageTk.PhotoImage(image)

# Add the image to the canvas
canvas.create_image(150, 150, image=photo)
'''

# create object
app = Application(root)
app.mainloop()