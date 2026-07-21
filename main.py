import speech_recognition as sr
import pyttsx3
import webbrowser
import time
import musicLibrary
import pywhatkit
import requests
import os
import datetime
import psutil
import pyautogui
import tkinter as tk
import winsound
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities
import cv2
import winsound
import threading
import time
import re
import pythoncom
from ui.ui import JarvisUI


from plyer import notification

from client import client

from dotenv import load_dotenv
import os

ui = None



load_dotenv()
newsApi = os.getenv("NEWS_API_KEY")
weatherApi = os.getenv("WEATHER_API_KEY")

device = AudioUtilities.GetSpeakers()
volume = device.EndpointVolume

def speak(text):
    engine = pyttsx3.init()

    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[0].id)
    engine.setProperty("rate", 170)

    engine.say(text)
    engine.runAndWait()
    engine.stop()




def aiprocess(command):

    prompt = f"""
You are Jarvis, Suraj's personal AI voice assistant.

Rules:
- Reply in 2 to 4 short sentences.
- Keep answers under 50 words unless the user asks for a detailed explanation.
- Speak naturally like Alexa or Google Assistant.
- Do not use bullet points.
- Be friendly, intelligent, and concise.
- If someone asks a long question, give only a short summary.
- If the user says "explain in detail", then give a detailed answer.

User: {command}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",   # Replace with your working model if different
        contents=prompt
    )

    return response.text


def flash_screen():
    root = tk.Tk()

    root.attributes("-fullscreen", True)
    root.configure(bg="white")
    root.attributes("-topmost", True)

    # Flash for 120 milliseconds
    root.after(120, root.destroy)

    root.mainloop()



def get_weather(city):

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weatherApi}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()

        print("URL:", url)
        print("Status:", response.status_code)
        print("Response:", data)

        if response.status_code != 200:
            speak(f"Sorry, I couldn't find weather information for {city}.")
            return

        temperature = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        condition = data["weather"][0]["description"]

        weather_report = (
        f"Currently in {city.title()},"
        f"the temperature is {round(temperature)} degrees Celsius. "
        f"The weather is {condition}. "
        f"It feels like {round(feels_like)} degrees. "
        f"Humidity is {humidity} percent."
        )

        print(weather_report)
        speak(weather_report)

    except Exception:
        speak("Sorry, I couldn't fetch the weather right now.")



def confirm_action():
    speak("Are you sure? Please say yes or no.")
    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:

            print("Waiting for confirmation...")
            audio = r.listen(source, timeout=5)

        confirmation = r.recognize_google(audio).lower()
        print("Confirmation:", confirmation)

        if "yes" in confirmation:
            return True
        else:
            return False
    except Exception:
        speak("I didn't catch that.")
        return False



def take_photo():

    speak("Opening camera")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        speak("I could not access your camera")
        return

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )
    detected = False

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5
        )

        if len(faces) > 0:
            detected = True
            for (x, y, w, h) in faces:

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    3
                )

                cv2.putText(
                    frame,
                    "Face Detected",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

        else:
            cv2.putText(
                frame,
                "No Face Detected",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )
        cv2.imshow("Jarvis Camera", frame)
        key = cv2.waitKey(1)

        if detected:
            break

        if key == ord("q"):
            cap.release()
            cv2.destroyAllWindows()
            speak("Cancelled")
            return

    speak("Smile")
    # Countdown
    for count in ["3", "2", "1"]:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)

        cv2.putText(
            frame,
            count,
            (270, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            4,
            (0, 0, 255),
            6
        )
        cv2.imshow("Jarvis Camera", frame)
        cv2.waitKey(1000)

    # White Flash
    flash = frame.copy()
    flash[:] = (255, 255, 255)
    cv2.imshow("Jarvis Camera", flash)
    cv2.waitKey(120)
    # Camera Shutter Sound
    winsound.MessageBeep()

    # Capture a NEW clean frame (without countdown)
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    # Optional: Brighten image slightly
    frame = cv2.convertScaleAbs(frame, alpha=1.15, beta=15)
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpg"
    desktop = os.path.join(
        os.path.expanduser("~"),
        "OneDrive",
        "Desktop"
    )

    filepath = os.path.join(desktop, filename)
    cv2.imwrite(filepath, frame)
    speak("Photo saved successfully")
    cap.release()
    cv2.destroyAllWindows()


# timer&alarm

def start_timer(seconds):
    print("START TIMER CALLED:", seconds)
    speak(f"Timer started for {seconds} seconds.")
    def timer():
        time.sleep(seconds)
        notification.notify(
        title="⏰ Timer Finished",
        message="Your timer has completed.",
        app_name="Jarvis",
        timeout=5
        )
        for i in range(5):
            winsound.MessageBeep()
            time.sleep(0.5)

        speak("Time's up Surajj.")
    threading.Thread(target=timer, daemon=True).start()



# ALL Features..

def processcommand(c):
    c = c.lower()

    if "open google" in c:
        webbrowser.open("https://google.com")

    elif "open facebook" in c:
        webbrowser.open("https://facebook.com")

    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")

    elif "open linkedin" in c:
        webbrowser.open("https://linkedin.com")

    elif "open github" in c:
        webbrowser.open("https://github.com")

    elif "open gpt" in c:
        webbrowser.open("https://chatgpt.com")


    elif "open vscode" in c:
        speak("Opening Visual Studio Code")
        os.system("code")

    elif "open chrome" in c:
        speak("Opening Chrome")
        os.system("start chrome")

    elif "open whatsapp" in c:
        speak("Opening WhatsApp")
        os.system("start whatsapp:")

    elif "open files" in c or "open file explorer" in c:
        speak("Opening File Explorer")
        os.system("explorer")

    elif "open camera" in c:
        speak("Opening Camera")
        os.system("start microsoft.windows.camera:")

    elif "open cmd" in c or "open command prompt" in c:
        speak("Opening Command Prompt")
        os.system("start cmd")

    elif "open notepad" in c:
        speak("Opening Notepad")
        os.system("notepad")

        # Open Desktop
    elif "open desktop" in c:

        path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
        os.startfile(path)
        speak("Opening Desktop")


    # Open Downloads
    elif "open downloads" in c:

        path = os.path.join(os.path.expanduser("~"), "Downloads")
        os.startfile(path)
        speak("Opening Downloads")


    # Open Documents
    elif "open documents" in c:

        path = os.path.join(os.path.expanduser("~"), "Documents")
        os.startfile(path)
        speak("Opening Documents")


    # Open Pictures
    elif "open pictures" in c:

        path = os.path.join(os.path.expanduser("~"), "Pictures")
        os.startfile(path)
        speak("Opening Pictures")


    # Open Videos
    elif "open videos" in c:

        path = os.path.join(os.path.expanduser("~"), "Videos")
        os.startfile(path)
        speak("Opening Videos")


    # Open Music
    elif "open music" in c:

        path = os.path.join(os.path.expanduser("~"), "Music")
        os.startfile(path)
        speak("Opening Music")


    # Open Task Manager
    elif "open task manager" in c:

        speak("Opening Task Manager")
        os.system("taskmgr")


    # Lock Computer
    elif "lock computer" in c:

        speak("Locking your computer")
        os.system("rundll32.exe user32.dll,LockWorkStation")




    # Shutdown Computer
    elif "shutdown computer" in c or "shut down computer" in c:

        if confirm_action():
            speak("Shutting down your computer.")
            os.system("shutdown /s /t 5")
        else:
            speak("Shutdown cancelled.")



    # Restart Computer
    elif "restart computer" in c:
        if confirm_action():
            speak("Restarting your computer.")
            os.system("shutdown /r /t 5")
        else:
            speak("Restart cancelled.")
            
    
    # for time
    elif " current time" in c:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {current_time}")

    # for date
    elif "date" in c:
        current_date = datetime.datetime.now().strftime("%d %B %Y")
        speak(f"Today's date is {current_date}")    

    # it will show battery percentage
    elif "battery" in c:
        battery = psutil.sensors_battery()
        percent = battery.percent
        speak(f"Battery is at {percent} percent")



    elif "screenshot" in c:
        speak("Taking screenshot in")

        for i in ["3", "2", "1"]:
            speak(i)
            time.sleep(1)

        # Capture Screenshot
        screenshot = pyautogui.screenshot()

        # Flash Effect
        flash_screen()

        # Camera Sound
        winsound.MessageBeep()

        # Save to Desktop
        filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".png"

        path = os.path.join(
            os.path.expanduser("~"),
            "OneDrive",
            "Desktop",
            filename
        )
        screenshot.save(path)

        speak("Screenshot saved to Desktop")


    # used to increse the volume
    elif "increase volume" in c:
        current = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(
            min(current + 0.1, 1.0),
            None
        )
        speak("Volume increased")


    # used to decrese the volume
    elif "decrease volume" in c:
        current = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(
            max(current - 0.1, 0.0),
            None
        )
        speak("Volume decreased")



    # used to unmute
    elif "unmute volume" in c:
        volume.SetMute(0, None)
        speak("Volume unmuted") 


    # used to mute
    elif "mute volume" in c:
        volume.SetMute(1, None)
        speak("Volume muted")


    #used to max volume
    elif "maximum volume" in c:
        volume.SetMasterVolumeLevelScalar(
            1.0,
            None
        )
        speak("Maximum volume")


    #used to min volume  
    elif "minimum volume" in c:
        volume.SetMasterVolumeLevelScalar(
            0.0,
            None
        )
        speak("Minimum volume")

    # Set Volume to Specific Percentage
    elif "set volume to" in c:
        try:
            number = ''.join(filter(str.isdigit, c))
            if number:
                value = int(number)
                value = max(0, min(value, 100))
                volume.SetMasterVolumeLevelScalar(value / 100, None)
                speak(f"Volume set to {value} percent")
            else:
                speak("Please tell me the volume percentage.")
        except Exception:
            speak("Sorry, I couldn't set the volume.")    



    # brightness features

    # Increase Brightness
    elif "increase brightness" in c:
        current = sbc.get_brightness()[0]
        new = min(current + 10, 100)
        sbc.set_brightness(new)
        speak(f"Brightness increased to {new} percent")


    # Decrease Brightness
    elif "decrease brightness" in c:
        current = sbc.get_brightness()[0]
        new = max(current - 10, 10)
        sbc.set_brightness(new)
        speak(f"Brightness decreased to {new} percent")


    # Maximum Brightness
    elif "maximum brightness" in c or "full brightness" in c:
        sbc.set_brightness(100)
        speak("Brightness set to maximum")


    # Minimum Brightness
    elif "minimum brightness" in c:
        sbc.set_brightness(10)
        speak("Brightness set to minimum")


    # Current Brightness
    elif "current brightness" in c or "brightness level" in c:
        current = sbc.get_brightness()[0]
        speak(f"Current brightness is {current} percent")


    # Set Brightness to Specific Percentage
    elif "set brightness to" in c:

        try:
            number = ''.join(filter(str.isdigit, c))

            if number:
                value = int(number)
                value = max(10, min(value, 100))
                sbc.set_brightness(value)
                speak(f"Brightness set to {value} percent")

            else:
                speak("Please tell me the brightness percentage.")
        except Exception:
            speak("Sorry, I couldn't set the brightness.") 

    # used to get whether..

    elif "weather" in c:
        if "in" in c:
            city = c.split("in", 1)[1].strip()
            if city:
                get_weather(city)
            else:
                speak("Please tell me the city name.")
        else:
            get_weather("Pune")



    # used to search and play on youtube 
    elif c.startswith("play"):

        song = c.replace("play", "", 1).strip()
        if song in musicLibrary.music:

            speak(f"Playing {song}")
            webbrowser.open(musicLibrary.music[song])
        else:
            speak(f"Playing {song}")
            pywhatkit.playonyt(song)


    elif "news" in c:

        response = requests.get(
            "https://gnews.io/api/v4/top-headlines",
            params={
            "country": "in",
            "lang": "en",
            "max": 5,
            "apikey": newsApi
            }
        )

        if response.status_code == 200:

            data = response.json()

            speak("Here are today's top headlines.")

            for article in data["articles"]:
                print(article["title"])
                speak(article["title"])

        else:

            print(response.text)
            speak("Sorry, I couldn't fetch the news.")

    
    # used to take photo 
    elif "take my photo" in c or "take photo" in c:
        take_photo()

    # used to set timer
    elif "set timer" in c:
        print(">>> TIMER COMMAND DETECTED")
        c = c.lower()
        match = re.search(r"(\d+)", c)
        print(match)
        if match:
            value = int(match.group(1))
            print(value)
            if "minute" in c:
                seconds = value * 60
            elif "second" in c:
                seconds = value
            else:
                speak("Please say seconds or minutes.")
                return
            start_timer(seconds)
        else:
            speak("I could not understand the timer duration.")    


    # it will handel Genai process  
    else:
        output =aiprocess(c)
        speak(output)



# Start Jarvis

def start_jarvis(app_ui=None):

    global ui
    ui = app_ui

    pythoncom.CoInitialize()

    try:

        speak("Initializing Jarvis")

        while True:

            # Default state
            if ui:
                ui.root.after(0, ui.waiting)

            r = sr.Recognizer()

            try:
                # Listen for wake word
                with sr.Microphone() as source:

                    print("Listening...")

                    if ui:
                        ui.root.after(0, ui.listening)

                    r.adjust_for_ambient_noise(source, duration=1)
                    audio = r.listen(source, timeout=5, phrase_time_limit=3)

                print("Recognizing...")

                if ui:
                    ui.root.after(0, ui.processing)

                word = r.recognize_google(audio, language="en-IN")

                print("You said:", word)

                if ui:
                    ui.root.after(
                    0,
                    lambda: ui.update_command(f'Wake Word: "{word}"')
                    )

                # Wake Word
                if "jarvis" in word.lower():

                    print("Wake Word Detected")

                    if ui:
                        ui.root.after(0, ui.speaking)

                    speak("Yes Suraj")

                    # Listen for command
                    with sr.Microphone() as source:

                        print("Jarvis Active...")

                        if ui:
                            ui.root.after(0, ui.listening)

                        r.adjust_for_ambient_noise(source, duration=0.5)
                        audio = r.listen(source, timeout=5, phrase_time_limit=5)

                    print("Recognizing Command...")

                    if ui:
                        ui.root.after(0, ui.processing)

                    command = r.recognize_google(audio, language="en-IN")

                    print("Command:", command)
                    if ui:
                        ui.root.after(
                        0,
                        lambda: ui.update_command(f'Command: "{command}"')
                    )


                    if ui:
                        ui.root.after(0, ui.executing)

                    processcommand(command)

                    if ui:
                        ui.root.after(0, ui.waiting)

            except sr.WaitTimeoutError:
                print("No speech detected.")

                if ui:
                    ui.root.after(0, ui.waiting)

            except sr.UnknownValueError:
                print("Could not understand audio.")

                if ui:
                    ui.root.after(0, ui.waiting)

            except sr.RequestError as e:
                print("Google API Error:", e)

                if ui:
                    ui.root.after(0, ui.waiting)

            except Exception as e:
                print("Error:", e)

                if ui:
                    ui.root.after(0, ui.waiting)

    finally:
        pythoncom.CoUninitialize()