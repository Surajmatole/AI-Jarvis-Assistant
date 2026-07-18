import speech_recognition as sr
import pyttsx3
import webbrowser
import time
import musicLibrary
import pywhatkit
import requests
from client import client

from dotenv import load_dotenv
import os

load_dotenv()
newsApi = os.getenv("NEWS_API_KEY")

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

    # let genai handle the request..
    else:
        output =aiprocess(c)
        speak(output)




if __name__ == "__main__":

    speak("Initializing Jarvis")

    while True:

        r = sr.Recognizer()

        try:
            # Listen for wake word
            with sr.Microphone() as source:
                print("Listening...")
                r.adjust_for_ambient_noise(source, duration=1)
                audio = r.listen(source, timeout=5, phrase_time_limit=3)

            print("Recognizing...")
            word = r.recognize_google(audio, language="en-IN")

            print("You said:", word)

            # Wake word
            if "jarvis" in word.lower():

                print("Wake Word Detected")

                speak("Yes Suraj")

                # Listen for command
                with sr.Microphone() as source:
                    print("Jarvis Active...")
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    audio = r.listen(source, timeout=5, phrase_time_limit=5)

                print("Recognizing Command...")
                command = r.recognize_google(audio, language="en-IN")

                print("Command:", command)

                processcommand(command)

        except sr.WaitTimeoutError:
            print("No speech detected.")

        except sr.UnknownValueError:
            print("Could not understand audio.")

        except sr.RequestError as e:
            print("Google API Error:", e)

        except Exception as e:
            print("Error:", e)