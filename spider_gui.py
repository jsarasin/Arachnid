#!/usr/bin/python3
import tkinter as tk
from tkinter import ttk 

# from Arachnid import Arachnid,  Servo, Leg, now, ServoType, Gyro
class SpiderRender(tk.Frame):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.master.title("Lines")
        self.pack(expand=1)

        canvas = tk.Canvas(self)
        canvas.create_line(15, 25, 200, 25)
        canvas.create_line(300, 35, 300, 200, dash=(4, 2))
        canvas.create_line(55, 85, 155, 85, 105, 180, 55, 85)

        canvas.pack( expand=1)

class SpiderGUI:
    def __init__(self):
        self.direction = 1
        self.window = tk.Tk()
        self.window.resizable(width = 1, height = 1)
        # self.window['padding'] = (3,3,3,3)
        self.window['padx'] = 3
        self.window['pady'] = 3
        # self.gy = Gyro()

        gyro_frame = ttk.Frame(self.window, padding=(3,3,3,3))
        gyro_frame['relief'] = tk.GROOVE
        gyro_frame.pack(side = 'left')

        ttk.Label(gyro_frame, text = "Gyroscope").pack()

        pbxf = ttk.Frame(gyro_frame, padding=(3,3,3,3))
        ttk.Label(pbxf, text="X").pack(side = 'left')
        self.pbx = ttk.Progressbar(pbxf, orient='horizontal', length=200, mode='determinate')
        self.pbx['value'] = 50
        self.pbx.pack()
        pbxf.pack()

        pbyf = ttk.Frame(gyro_frame, padding=(3,3,3,3))
        ttk.Label(pbyf, text="Y").pack(side = 'left')
        self.pby = ttk.Progressbar(pbyf, orient='horizontal', length=200, mode='determinate')
        self.pby['value'] = 50
        self.pby.pack()
        pbyf.pack()

        self.move_progress()

    def move_progress(self):
        # self.pbx['value'] = self.gy.get_x_rotation() + 50
        # self.pby['value'] = self.gy.get_y_rotation() + 50

        self.window.after(10, self.move_progress)

spider = SpiderGUI()



# Calling mainloop 
spider.window.mainloop() 
