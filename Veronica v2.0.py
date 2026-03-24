#pip install pyttsx3 speechrecognition wikipedia sounddevice numpy scipy
# install each module sepertely
#for getting info must type or say according to wikipedia eg- "Sachin Tendulkar according to wikipedia"
#it can open any software just copy some commands and paste it change name and path
#its just basic assistance but its v2 bit inhanced than older

import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import threading
import tkinter as tk
import sounddevice as sd
from scipy.io.wavfile import write
import io
import re 

# --- Assistant Logic Class ---
class VaronikaAssistant:
    def __init__(self, display_callback):
        self.display_callback = display_callback
        self.engine_lock = threading.Lock()

    def speak(self, audio):
        """Thread-safe speech that cleans Wikipedia text before talking"""
        clean_audio = re.sub(r'\[.*?\]|\(.*?\)', '', audio) # Removes [1] and (listen)
        self.display_callback(f"Varonika: {clean_audio}")

        def run_speak():
            with self.engine_lock:
                try:
                    temp_engine = pyttsx3.init('sapi5')
                    voices = temp_engine.getProperty('voices')
                    if len(voices) > 1:
                        temp_engine.setProperty('voice', voices[1].id)
                    temp_engine.setProperty('rate', 180)
                    temp_engine.say(clean_audio)
                    temp_engine.runAndWait()
                    temp_engine.stop()
                except Exception as e:
                    print(f"Speech Error: {e}")

        threading.Thread(target=run_speak, daemon=True).start()

    def wishMe(self):
        hour = int(datetime.datetime.now().hour)
        greeting = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 17 else "Good Evening"
        self.speak(f"{greeting}, boss! I am Varonika. How can I help you?")

    def takeVoiceCommand(self):
        r = sr.Recognizer()
        fs, seconds = 44100, 5
        try:
            self.display_callback("Listening (5 seconds)...")
            recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()
            byte_io = io.BytesIO()
            write(byte_io, fs, recording)
            byte_io.seek(0)
            with sr.AudioFile(byte_io) as source:
                audio_data = r.record(source)
            query = r.recognize_google(audio_data, language='en-in')
            return query.lower()
        except:
            return "none"

    def process_query(self, query):
        if query == "none":
            self.display_callback("I didn't hear anything.")
            return

        self.display_callback(f"User: {query}")

        # 1. WIKIPEDIA
        if 'wikipedia' in query:
            self.speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            try:
                results = wikipedia.summary(query, sentences=2)
                self.speak(results)
            except: self.speak("I couldn't find that topic.")

        # 2. WEB BROWSERS
        elif 'open youtube' in query:
            self.speak("Opening Youtube")
            webbrowser.open("youtube.com")
        elif 'open google' in query:
            self.speak("Opening Google")
            webbrowser.open("google.com")
        elif 'open microsoft' in query:
            self.speak("Opening Edge")
            webbrowser.open("microsoftedge.com")

        # 3. LOCAL MEDIA (Your D: Drive Paths)
        elif 'play music' in query:
            music_dir = 'D:\\Non Critical\\songs'
            if os.path.exists(music_dir):
                songs = os.listdir(music_dir)
                self.speak(f"Playing {songs[0]}")
                os.startfile(os.path.join(music_dir, songs[0]))
            else: self.speak("Music folder not found on D drive.")

        elif 'play videos' in query:
            videos_dir = 'D:\\Non Critical\\videos'
            if os.path.exists(videos_dir):
                videos = os.listdir(videos_dir)
                self.speak(f"Playing video")
                os.startfile(os.path.join(videos_dir, videos[0]))
            else: self.speak("Video folder not found.")

        # 4. TIME
        elif 'tell me the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            self.speak(f"Boss, the time is {strTime}")

        # 5. APPS & TOOLS (Your Software Paths)
        elif 'open vs' in query:
            vsPath = r"C:\Users\HP\AppData\Local\Programs\Microsoft VS Code\Code.exe"
            self.speak("Opening VS Code")
            if os.path.exists(vsPath): os.startfile(vsPath)

        elif 'open dev' in query:
            devPath = r"C:\Program Files (x86)\Dev-Cpp\devcpp.exe"
            self.speak("Opening Dev C plus plus")
            if os.path.exists(devPath): os.startfile(devPath)

        elif 'open godot' in query:
            godotPath = r"C:\Users\HP\Downloads\Godot_v3.5.2-stable_win64.exe"
            self.speak("Opening Godot engine")
            if os.path.exists(godotPath): os.startfile(godotPath) 

        # 6. EXIT
        elif 'quit' in query or 'exit' in query:
            self.speak("Goodbye Boss, shutting down.")
            os._exit(0)
        
        else:
            self.speak("I am not programmed for that command yet.")

# --- UI Setup ---
class AssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Varonika Hybrid AI")
        self.root.geometry("460x600")
        self.root.configure(bg="#0f172a")

        self.assistant = VaronikaAssistant(self.update_label)

        tk.Label(root, text="VARONIKA v2.5", font=("Impact", 28), bg="#0f172a", fg="#22d3ee").pack(pady=20)
        
        self.status_label = tk.Label(root, text="Ready for commands...", wraplength=400, font=("Consolas", 10), 
                                     bg="#1e293b", fg="#e2e8f0", height=10, width=50, anchor="nw", padx=10, pady=10)
        self.status_label.pack(pady=10)

        self.entry_box = tk.Entry(root, font=("Segoe UI", 12), width=35, bg="#334155", fg="white", insertbackground="white")
        self.entry_box.pack(pady=10, ipady=4)
        self.entry_box.bind("<Return>", lambda e: self.start_text())

        btn_frame = tk.Frame(root, bg="#0f172a")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="🎤 VOICE", font=("Arial", 10, "bold"), command=self.start_voice, 
                  bg="#06b6d4", fg="white", width=12).grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="⌨ SEND", font=("Arial", 10, "bold"), command=self.start_text, 
                  bg="#64748b", fg="white", width=12).grid(row=0, column=1, padx=10)

        threading.Thread(target=self.assistant.wishMe, daemon=True).start()

    def update_label(self, text):
        self.status_label.config(text=text)

    def start_voice(self):
        def run():
            query = self.assistant.takeVoiceCommand()
            self.assistant.process_query(query)
        threading.Thread(target=run, daemon=True).start()

    def start_text(self):
        query = self.entry_box.get()
        if query:
            self.entry_box.delete(0, tk.END)
            threading.Thread(target=self.assistant.process_query, args=(query.lower(),), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = AssistantGUI(root)
    root.mainloop()