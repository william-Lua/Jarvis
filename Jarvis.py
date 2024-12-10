# Code for voice assistant and GUI 
import os
import threading
import time
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import tkinter as tk
from tkinter import messagebox
from openai import OpenAI

# OpenAI API key/back end
api_key = 'Api key'  # Replace with API key
client = OpenAI(api_key=api_key)
model = 'gpt-3.5-turbo'

# Set up the speech recognition and text-to-speech engines/back end
r = sr.Recognizer()
engine = pyttsx3.init()
voice = engine.getProperty('voices')[1]  # Set voice
engine.setProperty('voice', voice.id)

# GUI Setup/Front end
root = tk.Tk()
root.title("Voice Assistant JARVIS")
root.geometry("500x600")
root.configure(bg="#f5f5f5")  # Light background color

# Greeting Label
greeting = tk.Label(
    root, text="🤖 Hello! I'm JARVIS 🤖", font=("Helvetica", 20, "bold"), bg="#f5f5f5", fg="#00796b"
)
greeting.pack(pady=20)

# Input Section 
input_frame = tk.Frame(root, bg="#f5f5f5")
input_frame.pack(pady=10)

input_label = tk.Label(
    input_frame, text="Type Your Question Below:", font=("Helvetica", 16, "bold"), bg="#f5f5f5", fg="#d32f2f"
)
input_label.grid(row=0, column=0, columnspan=2, pady=5)

# Input box 
input_box = tk.Text(input_frame, font=("Helvetica", 14), height=5, width=30, bd=2, relief="solid", bg="#ffffff", fg="#000000")
input_box.grid(row=1, column=0, padx=10, pady=5)

# Bind the "Enter" key to process_input
def on_enter(event):
    process_input()

input_box.bind("<Return>", on_enter)  # Bind "Enter" key to the on_enter function

# Output Section
output_label = tk.Label(
    root, text="💬 Conversation:", font=("Helvetica", 14, "bold"), bg="#f5f5f5", fg="#00796b"
)
output_label.pack(pady=5)

output_frame = tk.Frame(root, bg="#f5f5f5")
output_frame.pack(pady=5)

output = tk.Text(
    output_frame, height=15, width=50, wrap="word", font=("Helvetica", 12), bg="#ffffff", fg="#000000", 
    bd=2, relief="solid", insertbackground="black"
)
output.pack(side=tk.LEFT, padx=10, pady=5)

output_scrollbar = tk.Scrollbar(output_frame, command=output.yview, bg="#ffffff")
output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
output.config(yscrollcommand=output_scrollbar.set)

# Clear Button
clear_button = tk.Button(
    root, text="Clear Conversation 🗑️", font=("Helvetica", 12), bg="#e53935", fg="white", command=lambda: clear_conversation(),
    activebackground="#c62828", activeforeground="white", relief="flat", width=20, height=1
)
clear_button.pack(pady=10)

# Footer Label
footer = tk.Label(
    root, text="Designed by William", font=("Helvetica", 10), bg="#f5f5f5", fg="#757575"
)
footer.pack(pady=10)

# Functions for handling inputs, speech, and interaction

# Process typed input/back end
def process_input():
    user_text = input_box.get("1.0", tk.END).strip()  # Get text from the Text box
    if user_text:  # Ensure input is not empty
        output.insert(tk.END, f"\nUser: {user_text}\n", 'user')  # Display user input
        input_box.delete("1.0", tk.END)  # Clear the entry box
        
        # Send to OpenAI for processing
        response = get_openai_response(user_text)
        output.insert(tk.END, f"JARVIS: {response}\n", 'jarvis')
        speak(response)
    else:
        messagebox.showwarning("Warning", "Please enter some text!")

# Function to clear conversation/front end
def clear_conversation():
    output.delete(1.0, tk.END)  # Clear all text in the output box

# Get OpenAI response/back end
def get_openai_response(command):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": command}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Speak a given text/back end
def speak(text):
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save("response.mp3")
    os.system("mpg123 response.mp3")  # Play the response audio using mpg123

# Listen for the "Hey Jarvis" wake word/back end
def listen_for_wake_word():
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        while True:
            try:
                print("Listening for 'Hey Jarvis'...")
                audio = r.listen(source)  
                command = r.recognize_google(audio).lower()
                print(f"Detected: {command}")

                if "hey jarvis" in command:
                    output.insert(tk.END, "JARVIS: Wake word detected. Listening for commands...\n")
                    output.yview(tk.END)
                    listen_and_respond()

            except sr.UnknownValueError:
                print("Wake word not detected.")
            except sr.RequestError as e:
                output.insert(tk.END, f"JARVIS: Error: {e}\n")
                print(f"Error: {e}")

# Listen for commands after "Hey Jarvis" is detected/front end
def listen_and_respond():
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Listening for command...")

        try:
            audio = r.listen(source, timeout=30)
            command = r.recognize_google(audio)
            print(f"Command received: {command}")

            output.insert(tk.END, f"User: {command}\n", 'user')  # Display user input
            response = get_openai_response(command)
            output.insert(tk.END, f"JARVIS: {response}\n", 'jarvis')
            speak(response)

        except sr.UnknownValueError:
            output.insert(tk.END, "JARVIS: Could not understand the command.\n")
            print("Could not understand the command.")
        except sr.RequestError as e:
            output.insert(tk.END, f"JARVIS: Error: {e}\n")
            print(f"Error: {e}")

# Function to start listening for the wake word in a separate thread
def start_wake_word_listener():
    threading.Thread(target=listen_for_wake_word, daemon=True).start()

# Run the GUI
def run_gui():
    start_wake_word_listener()
    root.mainloop()

# Color coding the User and JARVIS text in the conversation box
def add_tags():
    output.tag_configure('user', foreground='blue')  # Color for User
    output.tag_configure('jarvis', foreground='green')  # Color for JARVIS

if __name__ == "__main__":
    add_tags()  
    run_gui()
