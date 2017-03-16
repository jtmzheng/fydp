import time
import sys

import Tkinter
from Tkinter import *
import math
import threading

from  client import *
from  monitor import *

from PIL import Image, ImageTk

MAX_CHUNK_SIZE = 4096
DEFAULT_HOSTNAME = '192.168.7.2'
DEFAULT_HOSTNAME_2 = '192.168.8.2'
DEFAULT_PORT = 5555

SOUND_THRESHOLD = 300;

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 600

array_dist = 2
num_mics = 2

ND = 6
TND = WINDOW_HEIGHT/ND

baseHeight0 = 0.7 * ND * TND
baseWidth0 = WINDOW_WIDTH/2 - TND * array_dist / 2

baseHeight1 = 0.7 * ND * TND
baseWidth1 = WINDOW_WIDTH/2 + TND * array_dist / 2

angle0 = 45
angle1 = 0
radius = WINDOW_HEIGHT

#  import MIC symbol
image = Image.open('microphone.png')
image = image.resize((50, 50), Image.ANTIALIAS)


class GUI(threading.Thread):
    def __init__(self):
        self.prev_mic_0 = []
        self.prev_mic_1 = []
        self.line_0 = None
        self.line_1 = None
        self.cur_mic_0 = None
        self.cur_mic_1 = None

    def draw_mics(self, A0, A1):
        #  import MIC symbol
        print('----')
        print(num_mics)
        micIcon = ImageTk.PhotoImage(image)
        A0C = baseWidth0, baseHeight0
        A1C = baseWidth1, baseHeight1
        self.C.coords(A0, A0C)
        self.C.coords(A1, 9999999,9999999)
        if num_mics == 2:
            self.C.coords(A1, A1C)

    def draw_lines(self, A0, A1):
        if self.line_0 != None:
            self.prev_mic_0.append(self.cur_mic_0)
        if self.line_1 != None:
            self.prev_mic_1.append(self.cur_mic_1)

        self.C.delete('line')
        self.line_0 = None
        self.line_1 = None

        # Mic 0 Line
        self.cur_mic_0 = baseWidth0, baseHeight0, baseWidth0 + radius * math.sin(math.radians(A0)), baseHeight0 - radius * math.cos(math.radians(A0))
        self.line_0 = self.C.create_line(self.cur_mic_0, fill='#FFE800', width=5, arrow = Tkinter.LAST, smooth=True, tag='line')
        if num_mics == 2:
            # Mic 1 Line
            self.cur_mic_1 = baseWidth1, baseHeight1, baseWidth1 + radius * math.sin(math.radians(A1)), baseHeight1 - radius * math.cos(math.radians(A1))
            self.line_1 = self.C.create_line(self.cur_mic_1, fill='#FFE800', width=5, arrow = Tkinter.LAST, smooth=True, tag='line')

        # Draw 'ghost' lines
        for mic in self.prev_mic_0:
            self.C.create_line(mic, fill='#FFFFFF', width=2, arrow=Tkinter.LAST, smooth=True, tag='line', dash=(3,5))
        for mic in self.prev_mic_1:
            self.C.create_line(mic, fill='#FFFFFF', width=2, arrow=Tkinter.LAST, smooth=True, tag='line', dash=(3,5))

    def update_arrays(self, A0, A1):
        global num_mics
        global baseWidth0
        global baseWidth1
        num_mics = int(self.NumArrayEntry.get())
        array_dist = int(self.DistanceEntry.get())

        if num_mics == 1:
            baseWidth0 = WINDOW_WIDTH/2
        elif num_mics == 2:
            baseWidth0 = WINDOW_WIDTH/2 - TND * array_dist/2
            baseWidth1 = WINDOW_WIDTH/2 + TND * array_dist/2

        #self.draw_mics(A0, A1)
        self.draw_lines(A0, A1)
        self.C.pack()

    def callback(self):
        self.top.quit()

    def runMonitor(self):
        for i in range(int(self.NumRunEntry.get())):
            m = Monitor(SOUND_THRESHOLD, 1)
            m.add_callback('[MultiBeagleReader::read]', self.mbr.read)
            ret_angles = m.monitor()
            self.update_arrays(360-math.degrees(ret_angles[0]), 360-math.degrees(ret_angles[1]))
            self.top.update_idletasks()
            self.top.update()

    def run(self):
        #self.br_1 = BeagleReader(DEFAULT_HOSTNAME, DEFAULT_PORT, x=0, y=0, l=0.3, samples=0)
        #self.br_2 = BeagleReader(DEFAULT_HOSTNAME_2, DEFAULT_PORT, x=array_dist, y=0, l=0.3, samples=0)

        #For Linux testing
        self.br_1 = BeagleReader('localhost', 5555, x=0, y=0, l=0.3, samples=0)
        self.br_2 = BeagleReader('localhost', 5556, x=array_dist, y=0, l=0.3, samples=0)

        self.mbr = MultiBeagleReader([self.br_1, self.br_2], 0, 0, 100, '')

        ######## Global Tkinter things that are important
        self.top = Tkinter.Tk()

        # Canvas for main Vizulization
        self.C = Tkinter.Canvas(self.top, bg='#7373D9', height=WINDOW_HEIGHT, width=WINDOW_WIDTH)

        # Mic 0 Line
        self.cur_mic_0 = baseWidth0, baseHeight0, baseWidth0 + radius * math.sin(math.radians(angle0)), baseHeight0 - radius * math.cos(math.radians(angle0))
        self.line_0 = self.C.create_line(self.cur_mic_0, fill='#FFE800', width=5, arrow=Tkinter.LAST, smooth=True, tag='line')

        # Mic 1 Line
        self.cur_mic_1 = baseWidth1, baseHeight1, baseWidth1 + radius * math.sin(math.radians(angle1)), baseHeight1 - radius * math.cos(math.radians(angle1))
        self.line_1 = self.C.create_line(self.cur_mic_1, fill='#FFE800', width = 5, arrow = Tkinter.LAST, smooth=True, tag='line')

        micIcon = ImageTk.PhotoImage(image)
        A0 = self.C.create_image((baseWidth0, baseHeight0), image = micIcon,tag='mic')
        A1 = self.C.create_image((baseWidth1, baseHeight1), image = micIcon,tag='mic')

        example = Tkinter.Label(self.top, text='Sonotrack Viz', font='Avenir\bNext', width=20, bg = '#090974', foreground = '#FFE800')
        example.place(relx=0.5, rely=0.1, anchor='c', )

        # Create the grid
        for i in range(0, WINDOW_WIDTH, int(WINDOW_HEIGHT/ND)):
            self.C.create_line([(i, 0), (i, WINDOW_HEIGHT)], tag='grid_line')
            self.C.create_line([(0, i), (WINDOW_WIDTH, i)], tag='grid_line')

        self.C.pack()
        # self.C.bind('<Configure>', self.create_grid)

        ####### Button Setup
        MyButton1 = Button(self.top, text='Run', width=10, command=self.runMonitor, bg = 'white', relief=GROOVE)
        MyButton1.place(relx=0.25, rely=0.95, anchor='c')

        MyButton2 = Button(self.top, text='Update', width=10, command=lambda: self.update_arrays(self.DistanceEntry, self.NumArrayEntry, A0, A1), bg = 'white')
        MyButton2.place(relx=0.5, rely=0.95, anchor='c')

        MyButton3 = Button(self.top, text='Quit', width=10, command=self.callback,bg = 'white')
        MyButton3.place(relx=0.75, rely=0.95, anchor='c')

        self.DistanceEntry = Tkinter.Entry(self.top,  width = 8)
        self.DistanceEntry.insert(END, '2')
        self.DistanceEntry.place(x=WINDOW_HEIGHT/4, y=WINDOW_HEIGHT/10*8.5, anchor='c')

        DistanceText = Tkinter.Label(self.top, text='Array Distance', font='Avenir\bNext', background = '#090974', fg = 'white', height = 1)
        DistanceText.place(x=WINDOW_HEIGHT/4, y=WINDOW_HEIGHT/5 *4, anchor='c')

        self.NumArrayEntry = Tkinter.Entry(self.top, width = 8)
        self.NumArrayEntry.insert(END, '2')
        self.NumArrayEntry.place(x=WINDOW_HEIGHT/5*2.5, y=WINDOW_HEIGHT/10*8.5, anchor='c')

        NumArrayText = Tkinter.Label(self.top, text='# Of Arrays', font='Avenir\bNext', background = '#090974', fg = 'white', height = 1)
        NumArrayText.place(x=WINDOW_HEIGHT/2, y=WINDOW_HEIGHT/5 *4, anchor='c')

        self.NumRunEntry = Tkinter.Entry(self.top, width = 8)
        self.NumRunEntry.insert(END, '2')
        self.NumRunEntry.place(x=WINDOW_HEIGHT/4*3, y=WINDOW_HEIGHT/10*8.5, anchor='c')

        NumRunText = Tkinter.Label(self.top, text='# of Runs', font='Avenir\bNext', background = '#090974', fg = 'white', height = 1)
        NumRunText.place(x=WINDOW_HEIGHT/4*3, y=WINDOW_HEIGHT/5 *4, anchor='c')

        self.top.mainloop()


gui = GUI()
gui.run()
