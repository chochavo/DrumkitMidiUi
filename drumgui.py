import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Progressbar
from tkinter import *
from PIL import ImageTk, Image
import numpy as np
import serial
import glob

def run_executable(path):
    os.system(path)

    #     choices = ['Production', 'QA']
    #     self.variable = StringVar(self)
    #     self.variable.set(choices[0])
    #     # self.list = OptionMenu(self, self.variable, *choices, command=print_x)
    #     self.list = OptionMenu(self, self.variable, *choices)
    #     self.img = ImageTk.PhotoImage(Image.open("capsuled.png"))
    #     self.panel = Label(self, image=self.img)
    #     self.tx = tk.Label(self)
    #     self.e1 = tk.Entry(self)
    #     self.l1 = tk.Label(self)
    #     self.l2 = tk.Label(self)
    #     self.exit_button = tk.Button(self)
    #     self.start_button = tk.Button(self, command=lambda: self.start_pressed(self.e1.get(), self.variable.get()))
    #     self.master = master
    #     tk.ANCHOR = "center"
    #     self.pack(side="top", expand=0, anchor="c")
    #     self.create_widgets()
    #
    # def hide_button(self):
    #     self.exit_button.destroy()
    #
    # def create_widgets(self):
    #     self.grid_columnconfigure(0, weight=1)
    #     self.grid_rowconfigure(0, weight=1)
    #
    #     self.tx["text"] = "Capsuled Flashing Tool, Revision: V2.0.1 - Jan. 2020"
    #     self.tx.config(font=("Arial", 12))
    #
    #     self.l1["width"] = 15
    #     self.l1["height"] = 1
    #     self.l1["text"] = 'Device ID'
    #
    #     self.l2["width"] = 15
    #     self.l2["height"] = 1
    #     self.l2["text"] = 'API Type'
    #
    #     self.e1["bd"] = 5
    #
    #     self.start_button["text"] = "Start"
    #     self.start_button["width"] = 15
    #     self.start_button["height"] = 1
    #
    #     self.exit_button["text"] = "Exit"
    #     self.exit_button["fg"] = "red"
    #     self.exit_button["command"] = self.exit_pressed
    #     self.exit_button["width"] = 15
    #     self.exit_button["height"] = 1
    #
    #     self.tx.grid(row=0, column=0, columnspan=3)
    #     self.l1.grid(sticky=E)
    #     self.l2.grid(sticky=E)
    #     self.e1.grid(row=1, column=1)
    #     self.list.grid(row=2, column=1)
    #     self.panel.grid(row=1, column=2, columnspan=2, rowspan=2, sticky=W + E + N + S, padx=5, pady=5)
    #     self.start_button.grid(row=3, column=2)
    #     self.exit_button.grid(row=3, column=3)
    #
    #     # self.exit_button.pack(side="right")
    #     # self.panel.pack(expand="yes")
    #     # self.start_button.pack(side="left")
    #     # self.e1.pack()  # side="right" # )
    #     # self.l2.pack()
    #     # self.l1.pack()
    #     # self.tx.pack()
    #     # self.list.pack()
    #
    # # APPLICATION SEQUENCE BEGINS HERE #
    # @staticmethod
    # def start_pressed(device_id, type_in):
    #     if not device_id.isdigit() or int(device_id, base=10) < 50000 or int(device_id, base=10) >= 60000 or \
    #             len(device_id) == 0:
    #         tk.messagebox.showerror('Wrong Device ID', 'Device ID must be in range between 50000 and 59999',
    #                                 icon='error')
    #     else:
    #         if save_configuration(device_id, type_in) != -1:
    #             DeviceSettings.device_id = device_id
    #             DeviceSettings.api_type = type_in
    #             interactive_sequence()
    #
    # @staticmethod
    # def exit_pressed():
    #     msg_box = tk.messagebox.askquestion('Exit Application', 'Are you sure you want to quit?',
    #                                         icon='warning')
    #     if msg_box == 'yes':
    #         exit()


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        # GUI Image for drum note selection
        self.img = ImageTk.PhotoImage(Image.open("drumkit.png"))
        self.panel = Label(self, image=self.img)

        # Buttons
        self.connect_button = tk.Button(self, command=lambda: self.connect_pressed())
        self.programming_button = tk.Button(self, command=lambda: self.start_arduino_data_exchange())
        self.exit_button = tk.Button(self, command=lambda: self.exit_pressed())
        self.save_config_button = tk.Button(self, command=lambda: self.save_config_pressed())
        self.w1 = Scale(None, from_=127, to=0, tickinterval=0, orient=HORIZONTAL)

        # Main ROOT window
        self.master = master
        tk.ANCHOR = "center"

        # Creating widgets
        self.connect_button["text"] = "Start"
        self.connect_button["width"] = 15
        self.connect_button["height"] = 1

        self.programming_button["text"] = "Start"
        self.programming_button["width"] = 15
        self.programming_button["height"] = 1

        self.exit_button["text"] = "Exit"
        self.exit_button["fg"] = "red"
        self.exit_button["width"] = 15
        self.exit_button["height"] = 1

        self.save_config_button["text"] = "Exit"
        self.save_config_button["fg"] = "red"
        self.save_config_button["width"] = 15
        self.save_config_button["height"] = 1

        self.w1["length"] = 500
        self.w1.set(100)
        self.w1["showvalue"] = 1

        self.pack(side="top", expand=0, anchor="c")
        # self.panel.grid(row=1, column=2, columnspan=2, rowspan=2, sticky=W + E + N + S, padx=5, pady=5)
        self.panel.pack()
        self.programming_button.pack(side="left", padx=20)
        self.connect_button.pack(side="right", padx=20)
        self.w1.pack()

    def start_pressed(self):
        print("Connect")

    def get_velocity(self):
        vel = self.w1.get()
        print(vel)




def interactive_sequence():
    tk.messagebox.showinfo('CFT V2.0.0', 'Attach magnetic flash tool to device')
    tk.messagebox.showinfo('CFT V2.0.0', 'Connect USB cable to device')
    tk.messagebox.showinfo('CFT V2.0.0', 'Flash Android 7.1.2 images with QFIL Tool')
    run_executable(paths.QFIL_PATH)
    msg = tk.messagebox.askquestion('CFT V2.0.0', 'Successful flashing?', icon='warning')
    if msg != 'yes':
        tk.messagebox.showinfo('CFT V2.0.0', 'Install failed', icon='error')
    else:
        tk.messagebox.showinfo('CFT V2.0.0', 'Remove magnetic flash tool from device')
        tk.messagebox.showinfo('CFT V2.0.0', 'Reconnect USB cable and attach battery to device')
        w = 900
        l = 100
        x = (int(get_monitor_info("width")) - w) / 2
        y = (int(get_monitor_info("height")) - l) / 2
        x_position = str(x)[0:str(x).find(".")]
        y_position = str(y)[0:str(y).find(".")]
        root_progress = tk.Tk()
        root_progress.lift()
        root_progress.resizable(0, 0)
        root_progress.geometry(str(w) + "x" + str(l) + "+" + x_position + "+" + y_position)
        root_progress.title('Capsuled Flashing Tool')
        canvas1 = tk.Canvas(root_progress, width=400, height=50, relief='raised')
        progress = Progressbar(root_progress, orient=HORIZONTAL, length=800, mode='determinate')
        progress.pack(pady=10)
        main_flashing_sequence(root_progress, canvas1, progress)
        root_progress.mainloop()


def get_monitor_info(requested_dim):
    from screeninfo import get_monitors
    m = str(get_monitors())
    m = m.split('DISPLAY')
    # print("m[0]:" + m[0])
    y_index = str.find(m[0], "height=")
    x_index = str.find(m[0], "width=")
    h = m[0][y_index + 7:y_index + 12]
    w = (m[0][x_index + 6: x_index + 12])
    a = str.find(h, ",")
    b = str.find(w, ",")
    h = h[0:a]
    w = w[0:b]
    print("h: " + h, "w:" + w)
    if requested_dim == "width":
        return w
    else:
        return h


def drumkit_gui():
    root = tk.Tk()
    root.resizable(0, 0)
    app = Application(master=root)
    app.master.title("Roll-Up MIDI Drumkit V1.0")
    width = int(get_monitor_info("width"))
    length = int(get_monitor_info("height"))
    x = width / 4
    y = length / 4
    x_position = str(x)[0:str(x).find(".")]
    y_position = str(y)[0:str(y).find(".")]
    window_width = str(width / 2)[0:str(width / 2).find(".")]
    window_length = str(length / 2.4)[0:str(length / 2.4).find(".")]
    geo = window_width + "x" + window_length + "+" + x_position + "+" + y_position
    print("Main GUI geometry: " + geo)
    # app.master.geometry(geo)
    root.bind("<Button 1>", event_ui_clicked)
    app.mainloop()


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def init_serial_port():
    ser = serial.Serial()
    ser.baudrate = 57600
    ser.port = 'COM1'


def event_ui_clicked(event):
    x = event.x
    y = event.y
    print(x, y)
    rho, phi = cart2pol(x, y)
    if DrumsCoordinates.KICK[0] - DrumsCoordinates.KICK_RADIUS < x < DrumsCoordinates.KICK[0] + DrumsCoordinates.KICK_RADIUS:
        if DrumsCoordinates.KICK[1] - DrumsCoordinates.KICK_RADIUS < y < DrumsCoordinates.KICK[1] + DrumsCoordinates.KICK_RADIUS:
            print("Kick was pressed!")
    elif DrumsCoordinates.HIHAT[0] - (DrumsCoordinates.HIHAT_WIDTH / 2) < x < DrumsCoordinates.HIHAT[0] + (DrumsCoordinates.HIHAT_WIDTH / 2):
        if DrumsCoordinates.HIHAT[1] - (DrumsCoordinates.HIHAT_LENGTH / 2) < y < DrumsCoordinates.HIHAT[1] + (DrumsCoordinates.HIHAT_LENGTH / 2):
            print("Hi-Hat was pressed!")


def cart2pol(x, y):
    rho = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(y, x)
    return rho, phi

def pol2cart(self, rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return x, y

def getorigin(self, event):
    x = event.x
    y = event.y
    print(x, y)
    return x, y


class DrumsCoordinates:
    KICK = [323 , 268]
    HIHAT = [117, 115]
    SNARE = [205, 192]
    CRASH_1 = [173, 40]

    KICK_RADIUS = 60
    HIHAT_WIDTH = 145
    HIHAT_LENGTH = 60


if __name__ == '__main__':
    drumkit_gui()
    # print(serial_ports())

