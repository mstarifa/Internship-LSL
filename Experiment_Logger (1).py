"""
Imported compulsory library for gui interface and mouse, audio ,keyboard streaming data record

"""
import datetime
import os
import customtkinter
from tkinter import *
from tkinter import filedialog
import pytz
from pylsl import StreamInfo, StreamOutlet
from pynput import keyboard, mouse
import tkinter as tk
import wave
import time
import pylsl
import pyaudio
import threading

"""
create gui interface use tkinter library

"""

window = customtkinter.CTk()  # create root window
window.title("Basic GUI Layout")  # title of the GUI window
customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("green")

"""
create logger timestamp for record all task 

"""
# Variables to store user inputs
experiment_name = ""
participant_name = ""
folder_path = ""
file = ""

# Variables for timestamp logging
experiment_count = 0
task_count = 0
interval_count = 0
event_count = 0

experiment_end_count = 0
task_end_count = 0
interval_end_count = 0

timestamps = []


def log_timestamp(event):
    global experiment_count, task_count, interval_count, event_count
    global experiment_end_count, task_end_count, interval_end_count, event_start

    if event == "Experiment Start":
        experiment_count += 1
        event_start = "Start"
        event = f"Experiment {experiment_count} - {event_start}"
    elif event == "Experiment End":
        experiment_end_count += 1
        event_end = "End"
        event = f"Experiment End {experiment_end_count} - {event_end}"
    elif event == "Task Start":
        task_count += 1
        event_start = "Start"
        event = f"Task {task_count} - {event_start}"
    elif event == "Task End":
        task_end_count += 1
        event_end = "End"
        event = f"Task End {task_end_count} - {event_end}"
    elif event == "Interval Start":
        interval_count += 1
        event_start = "Start"
        event = f"Interval {interval_count} - {event_start}"
    elif event == "Event Start":
        event_count += 1
        event_start = "Start"
        event = f"Event {event_count} - {event_start}"

    current_time = datetime.datetime.now(pytz.timezone('Europe/Helsinki')).strftime("%Y-%m-%d %H:%M:%S")
    timestamps.append((event, current_time))

    text.insert(END, f"{event} at {current_time}\n")


def create_folder():
    global experiment_name, participant_name, folder_path, file
    experiment_name = experiment_name_entry.get()
    participant_name = participant_name_entry.get()
    folder_path = filedialog.askdirectory()
    folder_name = experiment_name + "/" + participant_name
    folder_path = os.path.join(folder_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    file = (participant_name + ".txt")
    Folder_path_entry.delete(0, END)  # Clear existing entry
    Folder_path_entry.insert(0, folder_path)
    text.insert(END, f"Experiment Name: {experiment_name}\n"
                     f"Participant Name: {participant_name}\n"
                     f"Folder Path: {folder_path}\n"
                     f"File: {file}\n\n\n")

    experiment_start_button.configure(state=tk.NORMAL)
    folder_button.configure(state=tk.DISABLED)
    experiment_name_entry.configure(state=tk.DISABLED)
    participant_name_entry.configure(state=tk.DISABLED)


# Function to start the experiment
def start_experiment():

    global experiment_start_button, experiment_end_button, interval_start_button, task_start_button, event_start_button
    experiment_start_button.configure(state=tk.DISABLED)
    experiment_end_button.configure(state=tk.NORMAL)
    interval_start_button.configure(state=tk.NORMAL)
    task_start_button.configure(state=tk.NORMAL)
    event_start_button.configure(state=tk.NORMAL)
    log_timestamp("Experiment Start")


def end_experiment():
    global experiment_start_button, experiment_end_button, interval_start_button, task_start_button, event_start_button
    experiment_end_button.configure(state=tk.DISABLED)
    interval_start_button.configure(state=tk.DISABLED)
    interval_end_button.configure(state=tk.DISABLED)
    task_start_button.configure(state=tk.DISABLED)
    task_end_button.configure(state=tk.DISABLED)
    experiment_start_button.configure(state=tk.NORMAL)
    log_timestamp("Experiment End")


def start_task():
    task_start_button.configure(state=tk.DISABLED)
    task_end_button.configure(state=tk.NORMAL)
    log_timestamp("Task Start")


def end_task():
    task_end_button.configure(state=tk.DISABLED)
    interval_start_button.configure(state=tk.NORMAL)
    log_timestamp("Task End")


def start_interval():
    interval_start_button.configure(state=tk.DISABLED)
    interval_end_button.configure(state=tk.NORMAL)
    log_timestamp("Interval Start")


def end_interval():
    interval_end_button.configure(state=tk.DISABLED)
    task_start_button.configure(state=tk.NORMAL)
    log_timestamp("Interval End")


def start_event():

    log_timestamp("Event Start")


def save_logged_info():
    filename = folder_path + "/" + participant_name + ".txt"
    with open(filename, "w") as file:
        file.write("Experiment Name: {}\n".format(experiment_name))
        file.write("Participant Name: {}\n".format(participant_name))
        file.write("Timestamp\t\t\tEvent\n")
        for timestamp in timestamps:
            file.write("{}\t{}\n".format(timestamp[1], timestamp[0]))

    print("Logged information saved to: {}".format(filename))
    text.insert(END, f"\nLogged information saved to: {filename}\n")

    experiment_name_entry.delete(0, END)
    participant_name_entry.delete(0, END)
    Folder_path_entry.delete(0, END)
    # Enable the experiment name and participant name entry fields
    experiment_name_entry.configure(state=tk.NORMAL)
    participant_name_entry.configure(state=tk.NORMAL)

    # Enable the folder button to create a new folder
    folder_button.configure(state=tk.NORMAL)


"""
create a method for  keyboard ,mouse and audio streaming data  record 

"""
file_path_1 = ""
keyboard_listener = None
mouse_listener = None
audio_thread = None
mouse_keyboard_thread = None
stop_event = threading.Event()

# Create LSL stream outlet for audio data
audio_info = StreamInfo('AudioData', 'Audio', 1, 44100, pylsl.cf_float32, 'audio_data')
audio_outlet = StreamOutlet(audio_info)


def record_audio(file_path_1):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []

    log_text("Started recording audio...")

    while not stop_event.is_set():
        data = stream.read(CHUNK)
        frames.append(data)

    log_text("Finished recording audio.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    current_time1 = datetime.datetime.now(pytz.timezone('Europe/Helsinki')).strftime("%Y-%m-%d %H_%M_%S")
    filename = f"audio_{current_time1}.wav"
    audio_file_path = os.path.join(file_path_1, filename)

    wf = wave.open(audio_file_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    reset_interface()


def mouse_keyboard_stream(file_path_1):
    global keyboard_listener, mouse_listener

    timestamp = datetime.datetime.now(pytz.timezone('Europe/Helsinki')).strftime("%Y-%m-%d %H_%M_%S")

    # File paths for keyboard and mouse recordings
    keyboard_file = os.path.join(file_path_1, f'keyboard_data_{timestamp}.txt')
    mouse_file = os.path.join(file_path_1, f'mouse_data_{timestamp}.txt')

    # Open the text files for writing
    keyboard_file_handle = open(keyboard_file, 'w')
    mouse_file_handle = open(mouse_file, 'w')

    def on_keyboard_press(key):
        timestamp2 = datetime.datetime.now(pytz.timezone('Europe/Helsinki')).strftime("%Y-%m-%d %H_%M_%S")
        # Log the key and timestamp
        log_data = f"Key Pressed: {key} at {timestamp2}\n"
        print(log_data)
        log_text(f"Key Pressed - {key} at {timestamp2}")

        # Write the data to the keyboard file
        keyboard_file_handle.write(log_data)
        keyboard_file_handle.flush()

    def on_keyboard_release(key):
        # Handle key release events if needed
        pass

    # Start listening for keyboard events
    keyboard_listener = keyboard.Listener(on_press=on_keyboard_press, on_release=on_keyboard_release)
    keyboard_listener.start()

    # Create an LSL outlet for mouse data
    info = StreamInfo('MouseData', 'Mouse', 2, 0, 'float32', 'mouse-id')
    outlet = StreamOutlet(info)

    def on_mouse_click(x, y, button, pressed):
        if pressed:
            timestamp_num = datetime.datetime.now(pytz.timezone('Europe/Helsinki'))
            timestamp3 = timestamp_num.strftime("%Y-%m-%d %H_%M_%S")

            # Log the mouse click coordinates and timestamp
            log_text(f"Mouse Click - x={x}, y={y} position at {timestamp3}")
            log_data = f"Mouse click at ({x}, {y}) position at  {timestamp3}\n"
            print(log_data)

            # Write the data to the mouse file
            mouse_file_handle.write(log_data)
            mouse_file_handle.flush()

            # Send the mouse data through LSL
            outlet.push_sample([x, y], timestamp_num.timestamp())

    # Start listening for mouse events
    mouse_listener = mouse.Listener(on_click=on_mouse_click)
    mouse_listener.start()
    log_text("Started recording mouse and keyboard events...")

    while not stop_event.is_set():
        time.sleep(0.1)

    # Stop the keyboard and mouse listeners
    keyboard_listener.stop()
    mouse_listener.stop()

    log_text("Finished recording mouse and keyboard events.")

    # Close the file handles
    keyboard_file_handle.close()
    mouse_file_handle.close()

    print("Recordings Data saved to", file_path_1)
    reset_interface()


def start_recording():
    global file_path_1, audio_thread, mouse_keyboard_thread

    file_path_1 = Folder_path_entry.get()

    if not os.path.isdir(file_path_1):

        return

    if audio_var.get() == 1:
        audio_thread = threading.Thread(target=record_audio, args=(file_path_1,))
        audio_thread.start()

    if keyboard_var.get() == 1 or mouse_var.get() == 1:
        mouse_keyboard_thread = threading.Thread(target=mouse_keyboard_stream, args=(file_path_1,))
        mouse_keyboard_thread.start()

    start_button.configure(state=DISABLED)  # Disable the start button while recording is in progress

    # Start the periodic GUI update check
    check_recording_status()


def stop_recording():
    global stop_event

    stop_event.set()


def check_recording_status():
    if audio_thread and audio_thread.is_alive():
        window.after(100, check_recording_status)  # Check again after 100 milliseconds
    elif mouse_keyboard_thread and mouse_keyboard_thread.is_alive():
        window.after(100, check_recording_status)  # Check again after 100 milliseconds


def reset_interface():
    global keyboard_listener, mouse_listener, stop_event

    if keyboard_listener:
        keyboard_listener.stop()

    if mouse_listener:
        mouse_listener.stop()

    stop_event.clear()

    check_audio.configure(state=NORMAL)
    check_keyboard.configure(state=NORMAL)
    check_mouse.configure(state=NORMAL)
    start_button.configure(state=NORMAL)


def log_text(text1):
    text.configure(state=tk.NORMAL)
    text.insert(tk.END, text1 + "\n")


"""
create gui interface for experiment logger and streaming data record

"""

width = window.winfo_screenwidth()
height = window.winfo_screenheight()
window.geometry("%dx%d" % (width, height))
window.title("Experiment Logger")


# Create left and right frames
left_frame = customtkinter.CTkFrame(window)
left_frame.pack(side=LEFT, padx=10, pady=5)

right_frame = customtkinter.CTkFrame(window)
right_frame.pack(side=LEFT, padx=10, pady=5)

enter_info = customtkinter.CTkLabel(left_frame, text="Experiment Logger", font=('Times New Roman', 24, 'bold'))
enter_info.grid(pady=12,padx=10, row=0, column=1)

output_preview_label = customtkinter.CTkLabel(right_frame, text="Output Preview", font=('Times New Roman', 24, 'bold'))
output_preview_label.pack(pady=12,padx=10)

text = Text(right_frame)
text.pack(fill=BOTH, expand=True)

# Expand the Text widget to fill the frame
experiment_name_label = customtkinter.CTkLabel(left_frame, text="Experiment Name:")
experiment_name_label.grid(row=1, column=1, padx=5, pady=5, sticky=E)
experiment_name_entry = customtkinter.CTkEntry(left_frame, placeholder_text="Experiment Name")
experiment_name_entry.grid(row=1, column=2, padx=10, pady=12)

participant_name_label = customtkinter.CTkLabel(left_frame, text="Participant Name:")
participant_name_label.grid(row=3, column=1, padx=5, pady=5, sticky=E)
participant_name_entry = customtkinter.CTkEntry(left_frame, placeholder_text="Participant Name")
participant_name_entry.grid(row=3, column=2, padx=10, pady=12)

Folder_path_label = customtkinter.CTkLabel(left_frame, text="Folder Path:" )
Folder_path_label.grid(row=4, column=1, padx=5, pady=5, sticky=E)
Folder_path_entry = customtkinter.CTkEntry(left_frame ,placeholder_text="Folder path")
Folder_path_entry.grid(row=4, column=2, padx=10, pady=12)

folder_button = customtkinter.CTkButton(left_frame, width=120,
                                 height=32,text="Create Folder", command=create_folder)
folder_button.grid(row=4, column=3, sticky=W, padx=5, pady=5)

enter_info = customtkinter.CTkLabel(left_frame, text="Timestamp Logging", font=('Times New Roman', 24, 'bold'))
enter_info.grid(row=5, column=1, padx=5, pady=5)

experiment_start_button = customtkinter.CTkButton(left_frame, text="Experiment Start", width=120,
                                 height=32,font=('Times New Roman', 15, 'bold'),fg_color='#58D68D',
                                 command=start_experiment, state=tk.DISABLED)
experiment_start_button.grid(row=6, column=1, padx=10, pady=12)

experiment_end_button = customtkinter.CTkButton(left_frame, text="Experiment End",width=120,
                                 height=32,font=('Times New Roman', 15, 'bold'), fg_color="#58D68D",
                               command=end_experiment, state=tk.DISABLED)
experiment_end_button.grid(row=6, column=2, padx=10, pady=12)


task_start_button = customtkinter.CTkButton(left_frame, text="Task Start", fg_color="#85C1E9",width=120,
                                 height=32, font=('Times New Roman', 15, 'bold'),command=start_task, state=tk.DISABLED)
task_start_button.grid(row=7, column=1, padx=10, pady=10)

task_end_button =  customtkinter.CTkButton(left_frame, text="Task End", fg_color="#85C1E9", width=120,
                                 height=32,font=('Times New Roman', 15, 'bold'),command=end_task, state=tk.DISABLED)
task_end_button.grid(row=7, column=2, padx=10, pady=10)


interval_start_button = customtkinter.CTkButton(left_frame, text="Interval Start",  width=120,
                                 height=32, font=('Times New Roman', 15, 'bold'),command=start_interval, state=tk.DISABLED)
interval_start_button.grid(row=8, column=1, padx=10, pady=10)

interval_end_button =customtkinter.CTkButton(left_frame, text="Interval End", width=120,
                                 height=32,font=('Times New Roman', 15, 'bold'),command=end_interval, state=tk.DISABLED)
interval_end_button.grid(row=8, column=2, padx=10, pady=10)

event_start_button = customtkinter.CTkButton(left_frame, text="Event", width=120,height=32, font=('Times New Roman', 15, 'bold'),command=start_event, state=tk.DISABLED)
event_start_button.grid(row=9, column=1, padx=10, pady=10)

save_button = customtkinter.CTkButton(left_frame, text="Save",font=('Times New Roman', 15, 'bold'), width=120,height=32, command=save_logged_info)
save_button.grid(row=10, column=2, padx=10, pady=10)
enter_info = customtkinter.CTkLabel(left_frame, text="LSL Stream Recording", font=('Times New Roman', 24, 'bold'))
enter_info.grid(row=13, column=1, padx=5, pady=5)

start_button = customtkinter.CTkButton(left_frame, text="Start Record", font=('Times New Roman', 15, 'bold'),fg_color="#03fc7b", width=120,height=32, command=start_recording)
start_button.grid(row=14, column=2, padx=10, pady=10)

stop_button = customtkinter.CTkButton(left_frame, text="Stop Record",font=('Times New Roman', 15, 'bold'),fg_color="#fc5203",width=120,height=32, command=stop_recording)
stop_button.grid(row=15, column=2, padx=10, pady=10)
# Checkboxes
audio_var = IntVar()
keyboard_var = IntVar()
mouse_var = IntVar()

check_audio = customtkinter.CTkCheckBox(left_frame, text="Audio", variable=audio_var)
check_audio.grid(row=14, column=1, sticky=W)

check_keyboard = customtkinter.CTkCheckBox(left_frame, text="Keyboard", variable=keyboard_var)
check_keyboard.grid(row=15, column=1, sticky=W)

check_mouse = customtkinter.CTkCheckBox(left_frame, text="Mouse", variable=mouse_var)
check_mouse.grid(row=16, column=1, sticky=W)

# Start GUI event loop
window.mainloop()
