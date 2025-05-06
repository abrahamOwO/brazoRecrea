import tkinter as tk
from tkinter import ttk
import serial
import time
import math

# === Setup serial connection ===
ser = serial.Serial('COM11', 9600, timeout=1)  # Change to your port
time.sleep(2)
print("✅ Serial connection established.")

# === Link lengths based on your measurements ===
L1 = 12.0        # Shoulder to elbow
L2 = 9.125       # Elbow to wrist 1
L3 = 9.0         # Wrist 2 to claw center
BASE_OFFSET_Z = 5.5 + 2.5
BASE_OFFSET_X = 1.5

# === Last sent values (to avoid spamming serial) ===
last_sent = {'A': None, 'B': None, 'C': None, 'D': None, 'E': None, 'F': None}

# === Helper functions ===

def send_command(label, value):
    try:
        value = int(float(value))
        if last_sent[label] != value:
            cmd = f"{label}:{value}\n"
            print("➡️", cmd.strip())
            ser.write(cmd.encode())
            last_sent[label] = value
    except ValueError as e:
        print(f"⚠️ Invalid value for {label}: {value} ({e})")

def set_home():
    for label in sliders:
        sliders[label].set(90)
        send_command(label, 90)
    x_slider.set(10)
    y_slider.set(0)
    z_slider.set(10)

def move_via_ik():
    try:
        x = float(x_slider.get()) - BASE_OFFSET_X
        y = float(y_slider.get())
        z = float(z_slider.get()) - BASE_OFFSET_Z

        r = math.sqrt(x**2 + y**2)
        base_angle = math.degrees(math.atan2(y, x))

        reach = math.sqrt(r**2 + z**2)
        if reach > (L1 + L2):
            print("⚠️ Target out of reach")
            return

        cos_angle_elbow = (L1**2 + L2**2 - reach**2) / (2 * L1 * L2)
        elbow_angle = math.degrees(math.acos(cos_angle_elbow))

        cos_angle_shoulder = (reach**2 + L1**2 - L2**2) / (2 * L1 * reach)
        shoulder_offset = math.degrees(math.acos(cos_angle_shoulder))
        shoulder_angle = math.degrees(math.atan2(z, r)) + shoulder_offset

        # Convert to servo-friendly range (0–180, where 90 = "real 0")
        servo_angles = {
            'A': int(90 + base_angle),
            'B': int(90 - shoulder_angle),
            'C': int(90 + elbow_angle),
            'D': 90,
            'E': 90,
            'F': 0
        }

        for label in ['A', 'B', 'C']:
            angle = max(0, min(180, servo_angles[label]))
            sliders[label].set(angle)
            send_command(label, angle)

    except Exception as e:
        print("❌ IK error:", e)

# === UI Setup ===
root = tk.Tk()
root.title("6-DOF Robot Arm Controller")

mainframe = ttk.Frame(root, padding="10")
mainframe.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

sliders = {}

for idx, label in enumerate(['A', 'B', 'C', 'D', 'E', 'F']):
    ttk.Label(mainframe, text=f"{label}").grid(row=idx, column=0, sticky=tk.W)
    sliders[label] = ttk.Scale(mainframe, from_=0, to=180, orient='horizontal',
                               command=lambda val, l=label: send_command(l, val))
    sliders[label].set(90)
    sliders[label].grid(row=idx, column=1)

ttk.Button(mainframe, text="Set Home", command=set_home).grid(row=6, column=0, columnspan=2, pady=5)

ttk.Label(mainframe, text="X (cm)").grid(row=7, column=0)
x_slider = ttk.Scale(mainframe, from_=-10, to=20, orient='horizontal')
x_slider.set(10)
x_slider.grid(row=7, column=1)

ttk.Label(mainframe, text="Y (cm)").grid(row=8, column=0)
y_slider = ttk.Scale(mainframe, from_=-15, to=15, orient='horizontal')
y_slider.set(0)
y_slider.grid(row=8, column=1)

ttk.Label(mainframe, text="Z (cm)").grid(row=9, column=0)
z_slider = ttk.Scale(mainframe, from_=0, to=25, orient='horizontal')
z_slider.set(10)
z_slider.grid(row=9, column=1)

ttk.Button(mainframe, text="Move via IK", command=move_via_ik).grid(row=10, column=0, columnspan=2, pady=5)

root.mainloop()
