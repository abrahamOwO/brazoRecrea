import serial
import tkinter as tk
from tkinter import ttk

# Set the correct COM port for your Bluetooth connection (change 'COM11' if needed)
COM_PORT = 'COM11'  # Replace with your actual COM port for the Bluetooth module
BAUD_RATE = 9600

# Set up serial communication
try:
    ser = serial.Serial(COM_PORT, BAUD_RATE)
    print("Serial connection established.")
except:
    print("No serial connection")
    ser = None

# Create a Tkinter window
root = tk.Tk()
root.title("Robot Arm Control")

# Define sliders for the servos
sliders = {}

# Function to send serial command to Arduino
def send_command(servo, value):
    command = f"{servo}:{value}\n"
    if(ser != None):
        ser.write(command.encode())  # Send command over serial
    print(f"Sent command: {command.strip()}")  # Print the command in terminal for troubleshooting

# Create sliders for each joint
def create_slider(label, servo, min_val, max_val):
    frame = ttk.Frame(root)
    frame.pack(pady=10)
    
    label = ttk.Label(frame, text=label)
    label.pack(side=tk.LEFT, padx=5)

    slider = ttk.Scale(frame, from_=min_val, to=max_val, orient='horizontal', length=200)
    slider.set((min_val + max_val) / 2)  # Start in the middle
    slider.pack(side=tk.LEFT, padx=5)
    
    # Store the slider in the dictionary
    sliders[servo] = slider

    # Add a function to send the value to the serial port when the slider is moved
    def on_slider_change(event):
        value = int(slider.get())
        send_command(servo, value)

    slider.bind("<Motion>", on_slider_change)

# Create buttons for home and stop actions
def create_home_button():
    def home():
        # Send home position commands to Arduino
        send_command("B", 0)  # Base to 90 degrees
        send_command("S", 0)  # Shoulder to 90 degrees
        send_command("E", 0)  # Elbow to 90 degrees
        send_command("W1", 0) # Wrist 1 to 90 degrees
        send_command("W2", 0) # Wrist 2 to 90 degrees
        send_command("C", 0)   # Claw to 0 degrees (closed)

        # Reset all sliders to their home positions (centered)
        sliders["B"].set(0)
        sliders["S"].set(0)
        sliders["E"].set(0)
        sliders["W1"].set(0)
        sliders["W2"].set(0)
        sliders["C"].set(0)

    home_button = ttk.Button(root, text="Set Home", command=home)
    home_button.pack(pady=10)
def create_straight_button():
    def extend():
        # Send home position commands to Arduino
        send_command("B", 90)  # Base to 90 degrees
        send_command("S", 90)  # Shoulder to 90 degrees
        send_command("E", 90)  # Elbow to 90 degrees
        send_command("W1", 90) # Wrist 1 to 90 degrees
        send_command("W2", 90) # Wrist 2 to 90 degrees
        send_command("C", 0)   # Claw to 0 degrees (closed)

        # Reset all sliders to their home positions (centered)
        sliders["B"].set(90)
        sliders["S"].set(90)
        sliders["E"].set(90)
        sliders["W1"].set(90)
        sliders["W2"].set(90)
        sliders["C"].set(0)

    straight_button = ttk.Button(root, text="Extend", command=extend)
    straight_button.pack(pady=10)

# Create sliders for each servo
create_slider("Base (B)", "B", 0, 180)
create_slider("Shoulder (S)", "S", 0, 180)
create_slider("Elbow (E)", "E", 0, 180)
create_slider("Wrist 1 (W1)", "W1", 0, 180)
create_slider("Wrist 2 (W2)", "W2", 0, 180)
create_slider("Claw (C)", "C", 0, 90)

# Create the Home button
create_home_button()
create_straight_button()

# Start the Tkinter event loop
root.mainloop()
