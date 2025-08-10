# communication.py
# Import needed files
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import serial, threading, time, sys

first_data_received = False

# Aetherlink variables
left_joystick_x = 512
left_joystick_y = 512
right_joystick_x = 512
right_joystick_y = 512

left_pot = 312
right_pot = 0
left_button = 0
right_button = 0
left_toggle_switch = 0
right_toggle_switch = 0

def read_arduino_setup(filename="arduino_files/arduino_setup.txt"):
    port = None
    baudrate = None
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("Port="):
                    port = line.split("=", 1)[1]
                elif line.lower().startswith("baudrate="):
                    baudrate = int(line.split("=", 1)[1])
    except FileNotFoundError:
        print(f"Setup file '{filename}' not found.")
    return port, baudrate

port, baud = read_arduino_setup()

arduino = None
if port is not None and baud is not None:
    try:
        arduino = serial.Serial(port=port, baudrate=baud, timeout=0.1)
    except serial.SerialException:
        print()
        arduino = None
else:
    print("Port or baudrate not set correctly in setup file.")

stop_communication_event = threading.Event()
communication_thread = None 

def read_from_arduino():
    global left_joystick_x, left_joystick_y, right_joystick_x, right_joystick_y
    global left_pot, right_pot, left_button, right_button
    global left_toggle_switch, right_toggle_switch
    global first_data_received

    if arduino is None:
        print("Arduino not connected, communication fail.")
        return

    while not stop_communication_event.is_set():
        try:
            line = arduino.readline().decode('utf-8').strip()
            if line:
                try:
                    (left_joystick_x, left_joystick_y, right_joystick_x, right_joystick_y,
                     left_pot, right_pot, left_button, right_button,
                     left_toggle_switch, right_toggle_switch) = map(int, line.split(','))
                    first_data_received = True
                except ValueError as ve:
                    print(f"Error parsing data: {ve} - Line: {line}")
        except serial.SerialException as e:
            print(f"Serial communication error: {e}")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
        time.sleep(0.01)

def start_communication_thread():
    global communication_thread, stop_communication_event
    if arduino is None:
        print()
        print("\033[91mCannot start communication - Arduino not connected.\033[0m")  
        print("\033[91mPlease connect the Arduino + NRF24L01 and restart the application (App will close in 15 seconds).\033[0m")  
        time.sleep(10)
        sys.exit(1)  # Exit immediately
    if communication_thread and communication_thread.is_alive():
        print("Communication thread already running.")
        return True
    stop_communication_event.clear()
    communication_thread = threading.Thread(target=read_from_arduino, daemon=True)
    communication_thread.start()
    print("Arduino communication started.")
    return True

def stop_communication_thread():
    global communication_thread, stop_communication_event
    stop_communication_event.set()
    if communication_thread:
        communication_thread.join(timeout=1)
    if arduino and arduino.is_open:
        arduino.close()
        print("Serial port closed.")