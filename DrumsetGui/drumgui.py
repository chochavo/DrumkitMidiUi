# KhomDrums V1.2.1
# Python UI Module
# April 2020

# Imported modules
import os
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import *
from PIL import ImageTk, Image
import numpy as np
import serial
import glob


# Hairless.exe handling thread
class ExternalExecutableThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        os.system("hairless.exe")


def run_hairless_executable():
    hairless = ExternalExecutableThread()
    hairless.start()


def set_active(ui):
    ui.grab_set()


def secondary_ui(drum_type):
    if drum_type == "Controller":
        run_hairless_executable()
    else:
        ui = tk.Tk()
        ui.resizable(0, 0)
        selection = SelectionUi(master=ui)
        selection.master.title("Roll-Up MIDI Drumkit V1.0")
        width = int(get_monitor_info("width"))
        length = int(get_monitor_info("height"))
        x = width / 8
        y = length / 8
        x_position = str((width / 2) - (x / 2))[0:str((width / 2) - (x / 2)).find(".")]
        y_position = str((length / 2) - (y / 2))[0:str((length / 2) - (y / 2)).find(".")]
        window_width = str(width / 7)[0:str(width / 7).find(".")]
        window_length = str(length / 7)[0:str(length / 7).find(".")]
        geo = window_width + "x" + window_length + "+" + x_position + "+" + y_position
        print("secondary_ui geometry: " + geo)
        selection.master.geometry(geo)
        selection.define_title(drum_type)
        selection.define_specific_values(drum_type)
        selection.create_widgets()
        selection.pass_root_value(ui)
        set_active(ui)
        selection.mainloop()


class SelectionUi(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.drum_type = tk.Label(self)
        self.note_label = tk.Label(self)
        self.pin_label = tk.Label(self)
        self.velocity_label = tk.Label(self)
        self.note_entry = tk.Entry(self)
        self.pin_entry = tk.Entry(self)
        self.velocity_entry = tk.Entry(self)
        self.drum_type.config(font='Helvetica 10 bold')
        self.accept = tk.Button(self, command=lambda: self.accept_pressed())
        self.cancel = tk.Button(self, command=lambda: self.cancel_pressed())

    def define_title(self, drum_type):
        self.drum_type["text"] = drum_type

    def pass_root_value(self, ui_in):
        self.ui = ui_in

    def define_specific_values(self, drum_type):
        self.drum_index = Drums.DRUM_ENUM.index(drum_type)
        self.note = Drums.DRUM_NOTES[self.drum_index]
        self.pin = Drums.DRUM_PINS[self.drum_index]
        self.velocity = Drums.DRUM_VELOCITIES[self.drum_index]

    def create_widgets(self):
        self.note_label["text"] = "Note"
        self.pin_label["text"] = "Arduino Pin"
        self.velocity_label["text"] = "Velocity"

        self.accept["text"] = "Accept"
        self.accept["fg"] = "green"
        self.accept["width"] = 10
        self.accept["height"] = 1

        self.cancel["text"] = "Cancel"
        self.cancel["fg"] = "red"
        self.cancel["width"] = 10
        self.cancel["height"] = 1

        self.note_entry["bd"] = 1
        self.note_entry.insert(END, self.note)
        self.note_entry["width"] = 3
        self.pin_entry["bd"] = 1
        self.pin_entry.insert(END, self.pin)
        self.pin_entry["width"] = 2
        self.velocity_entry["bd"] = 1
        self.velocity_entry.insert(END, self.velocity)
        self.velocity_entry["width"] = 3

        self.drum_type.grid(row=0, column=0, columnspan=2)
        self.note_label.grid(row=1, column=0, padx=5, pady=5)
        self.note_entry.grid(row=1, column=1, padx=5, pady=5)
        self.pin_label.grid(row=2, column=0, padx=5, pady=5)
        self.pin_entry.grid(row=2, column=1, padx=5, pady=5)
        self.velocity_label.grid(row=3, column=0, padx=5, pady=5)
        self.velocity_entry.grid(row=3, column=1, padx=5, pady=5)
        self.accept.grid(row=4, column=0, padx=5, pady=5)
        self.cancel.grid(row=4, column=1, padx=5, pady=5)

        self.pack(side="top", expand=0, anchor="c")

    def accept_pressed(self):
        if not self.note_entry.get().isdigit() or int(self.note_entry.get(), base=10) > 127 or int(
                self.note_entry.get(), base=10) < 0 \
                or len(self.note_entry.get()) == 0:
            tk.messagebox.showerror('Wrong Note!', 'Note must be in the range 0..127', icon='error')
        else:
            if not self.pin_entry.get().isdigit() or int(self.pin_entry.get(), base=10) > 20 or int(
                    self.pin_entry.get(), base=10) < 0 \
                    or len(self.pin_entry.get()) == 0:
                tk.messagebox.showerror('Wrong Pin!', 'Pin must be in the range 0..17', icon='error')
            else:
                if not self.velocity_entry.get().isdigit() or int(self.velocity_entry.get(), base=10) > 127 or int(
                        self.velocity_entry.get(), base=10) < 0 \
                        or len(self.velocity_entry.get()) == 0:
                    tk.messagebox.showerror('Wrong Velocity!', 'Velocity be in the range 0..17', icon='error')
                else:
                    Drums.DRUM_NOTES[self.drum_index] = int(self.note_entry.get())
                    Drums.DRUM_PINS[self.drum_index] = int(self.pin_entry.get())
                    Drums.DRUM_VELOCITIES[self.drum_index] = int(self.velocity_entry.get())
        self.ui.destroy()

    def cancel_pressed(self):
        self.ui.destroy()


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        # GUI Image for drum note selection
        self.img = ImageTk.PhotoImage(Image.open("drumkit.png"))
        self.panel = Label(self, image=self.img)
        self.tx = tk.Label(self)
        self.list_label = tk.Label(self)
        # Buttons
        self.connect_button = tk.Button(self, command=lambda: self.connect_pressed())
        self.load_config = tk.Button(self, command=lambda: self.load_config_pressed())
        self.exit_button = tk.Button(self, command=lambda: self.exit_pressed())
        self.save_config_button = tk.Button(self, command=lambda: self.save_config_pressed())
        self.program_device = tk.Button(self, command=lambda: self.program_device_pressed())
        self.w1 = Scale(None, from_=127, to=0, tickinterval=0, orient=HORIZONTAL)
        self.pack(side="top", expand=0, anchor="c")

        # COM Ports list
        choices = get_serial_ports()
        print(choices)
        self.variable = StringVar(self)
        self.variable.set(choices[0])
        # self.list = OptionMenu(self, self.variable, *choices, command=print_x)
        self.list = OptionMenu(self, self.variable, *choices)

        # Main ROOT window
        self.master = master
        tk.ANCHOR = "center"
        self.tx["text"] = "KhomDrums Programmer V1.2.1"
        self.tx.config(font='Tahoma 16 bold')

        # Creating widgets
        self.connect_button["text"] = "Refresh"
        self.connect_button["fg"] = "blue"
        self.connect_button["width"] = 15
        self.connect_button["height"] = 1

        self.program_device["text"] = "Program Device"
        self.program_device["fg"] = "green"
        self.program_device["width"] = 15
        self.program_device["height"] = 1

        self.exit_button["text"] = "Exit"
        self.exit_button["fg"] = "red"
        self.exit_button["width"] = 15
        self.exit_button["height"] = 1

        self.save_config_button["text"] = "Save Configuration"
        self.save_config_button["fg"] = "blue"
        self.save_config_button["width"] = 15
        self.save_config_button["height"] = 1

        self.load_config["text"] = "Load Configuration"
        self.load_config["fg"] = "red"
        self.load_config["width"] = 15
        self.load_config["height"] = 1

        self.w1["length"] = 500
        self.w1.set(100)
        self.w1["showvalue"] = 1

        self.list_label["width"] = 15
        self.list_label["height"] = 1
        self.list_label["text"] = 'Drum Kit COM Port'
        self.list_label.config(font='Helvetica 10 bold')

        self.tx.grid(row=0, column=0, columnspan=5)
        self.panel.grid(row=1, column=0, columnspan=5, rowspan=1, sticky=N, padx=5, pady=5)
        self.list_label.grid(row=2, column=0, columnspan=1)
        self.list.grid(row=2, column=1, columnspan=1)
        self.load_config.grid(row=2, column=2, columnspan=1)
        self.connect_button.grid(row=2, column=3, columnspan=1)
        self.save_config_button.grid(row=3, column=2, pady=20, padx=5, columnspan=1)
        self.program_device.grid(row=3, column=1, pady=20, padx=5, columnspan=1)
        self.exit_button.grid(row=3, column=3, pady=20, padx=5)

        self.connect_button_active = False

    def connect_pressed(self):
        print("Refresh pressed")
        choices = get_serial_ports()
        print(choices)
        self.variable = StringVar(self)
        self.variable.set(choices[0])
        # self.list = OptionMenu(self, self.variable, *choices, command=print_x)
        self.list = OptionMenu(self, self.variable, *choices)
        self.list.grid(row=2, column=1, columnspan=1)

    def exit_pressed(self):
        print("Exit Pressed")
        msg = tk.messagebox.askquestion('DrumKit MIDI', 'Are you sure you want to exit?', icon='info')
        if msg == 'yes':
            os.system("TASKKILL /F /IM hairless.exe")
            exit(0)

    def save_config_pressed(self):
        print("Saving configuration in txt format...")
        tk.messagebox.showinfo('DrumKit', "Configuration Saved")
        save_config()

    def load_config_pressed(self):
        print("Saving configuration in txt format...")
        tk.messagebox.showinfo('DrumKit', "Configuration Loaded")
        load_config()

    def get_velocity(self):
        vel = self.w1.get()
        print(vel)

    def program_device_pressed(self):
        tk.messagebox.showinfo('Programming Wizard', 'Press Kick and Hi-Hat pedals and OK', icon='info')
        print("selected COM PORT:" + self.variable.get())
        communicate_with_arduino(self.variable.get())


def save_config():
    f = open("config.txt", "w+")
    f.write("N=")
    for i in Drums.DRUM_NOTES:
        f.write(str(i) + ",")
    f.write("\n")
    f.write("P=")
    for i in Drums.DRUM_PINS:
        f.write(str(i) + ",")
    f.write("\n")
    f.write("V=")
    for i in Drums.DRUM_VELOCITIES:
        f.write(str(i) + ",")
    f.close()


def load_config():
    f = open("config.txt", "r")
    if f.mode == 'r':
        lines = f.readlines()
        note_string = lines[0]
        pin_string = lines[1]
        velocity_string = lines[2]
        note_string_t = note_string[2:].split(',')
        pin_string_t = pin_string[2:].split(',')
        velocity_string_t = velocity_string[2:].split(',')
        note_string_t.remove('\n')
        pin_string_t.remove('\n')
        velocity_string_t.remove('')
        notes = []
        pins = []
        velocities = []
        for i in note_string_t:
            notes.append(int(i))
        Drums.DRUM_NOTES = notes
        for i in pin_string_t:
            pins.append(int(i))
        Drums.DRUM_PINS = pins
        for i in velocity_string_t:
            velocities.append(int(i))
        Drums.DRUM_VELOCITIES = velocities
        print(Drums.DRUM_NOTES)
        print(Drums.DRUM_PINS)
        print(Drums.DRUM_VELOCITIES)


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
    app.master.title("KhomDrums")
    width = int(get_monitor_info("width"))
    length = int(get_monitor_info("height"))
    x = width / 2.5
    y = length / 1.7
    x_position = str(width / 2 - (x / 2))[0:str(width / 2 - (x / 2)).find(".")]
    y_position = str(length / 2 - (y / 2))[0:str(length / 2 - (y / 2)).find(".")]
    window_width = str(width / 2.5)[0:str(width / 2.5).find(".")]
    window_length = str(length / 1.7)[0:str(length / 1.2).find(".")]
    geo = window_width + "x" + window_length + "+" + x_position + "+" + y_position
    print("Main GUI geometry: " + geo)
    app.master.geometry(geo)
    root.bind("<Button 1>", event_ui_clicked)
    app.mainloop()


def get_serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
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


def communicate_with_arduino(port):
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port = port
    ser.timeout = 5
    try:
        ser.open()
        import time
        time.sleep(4)
        if ser.is_open:
            print(bytes(Drums.DRUM_NOTES))
            length = len(bytes(Drums.DRUM_NOTES))
            print(length)
            length += len(bytes(Drums.DRUM_PINS))
            print(length)
            length += len(bytes(Drums.DRUM_VELOCITIES))
            print(length)
            packet = bytes(Drums.DRUM_NOTES) + bytes(Drums.DRUM_PINS) + bytes(Drums.DRUM_VELOCITIES)
            print(packet)
            ser.write(packet)
            ser.flushInput()
            response = ser.readline()
            print(response)
            if str(response).__contains__("OK"):
                tk.messagebox.showinfo('Success', 'Data was transferred to Arduino successfully!', icon='info')
            else:
                tk.messagebox.showerror('COM Port Error', 'Idi v pizdu pidor ebuchii', icon='error')
        else:
            tk.messagebox.showerror('COM Port Error', 'Could not open ' + ser.port, icon='error')
    except (OSError, serial.SerialException):
        tk.messagebox.showerror('COM Port Error', 'Could not open ' + ser.port, icon='error')
    ser.close()


def event_ui_clicked(event):
    x = event.x
    y = event.y
    print(x, y)
    ui_index = 0
    while ui_index < len(Drums.DRUM_TYPES):
        if Drums.COORDINATES_X[ui_index] - (Drums.DIMS_WIDTH[ui_index] / 2) < x < Drums.COORDINATES_X[ui_index] + (
                Drums.DIMS_WIDTH[ui_index] / 2) \
                and Drums.COORDINATES_Y[ui_index] - (Drums.DIMS_LENGTH[ui_index] / 2) < y < Drums.COORDINATES_Y[ui_index] \
                + (Drums.DIMS_LENGTH[ui_index] / 2):
            print(Drums.DRUM_TYPES[ui_index])
            secondary_ui(Drums.DRUM_TYPES[ui_index])
        ui_index += 1


def getorigin(self, event):
    x = event.x
    y = event.y
    print(x, y)
    return x, y


class Drums:
    DRUM_TYPES = ["Kick", "Hihat", "Snare", "Crash 1", "Crash 2", "Tom High", "Tom Mid", "Tom Low", "Ride",
                  "Hihat Pedal", "Controller"]

    COORDINATES_X = [323, 117, 205, 173, 565, 271, 386, 488, 487, 135, 79]
    COORDINATES_Y = [268, 115, 192, 40, 29, 107, 104, 190, 71, 408, 208]
    DIMS_WIDTH = [60, 145, 130, 120, 120, 70, 70, 130, 120, 70, 145]
    DIMS_LENGTH = [60, 60, 80, 35, 35, 40, 40, 70, 35, 100, 50]

    DRUM_ENUM = ["Kick", "Snare", "Hihat", "Ride", "Crash 1", "Crash 2", "Tom High", "Tom Mid", "Tom Low", "Hihat Pedal"]
    DRUM_NOTES = [36, 40, 42, 51, 49, 55, 47, 45, 43, 48]
    DRUM_VELOCITIES = [110, 100, 100, 110, 110, 110, 110, 110, 110, 110]
    DRUM_PINS = [8, 6, 4, 3, 11, 9, 5, 10, 2, 7]


if __name__ == '__main__':
    drumkit_gui()
