# (1) Start
# (This part initializes the necessary libraries and sets up configurations.)

import os
from openai import OpenAI
from dotenv import load_dotenv
import time
import speech_recognition as sr
import pyttsx3
from gtts import gTTS

# Set the language for text-to-speech
language = 'en'

# Load environment variables
load_dotenv()

# Set your OpenAI API key
api_key = ('Enter API Key here')
client = OpenAI(api_key=api_key)

model = 'gpt-3.5-turbo'  # Specify the model to be used

# (2) Set up the speech recognition and text-to-speech engines
r = sr.Recognizer()
engine = pyttsx3.init("dummy")
voice = engine.getProperty('voices')[1]
engine.setProperty('voice', voice.id)

# Adjust for ambient noise
with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source)

def listen_and_respond(source):
    print("Listening for wake word...")
    while True:
        try:
            audio = r.listen(source, timeout=30)  # Increased timeout to 30 seconds
            text = r.recognize_google(audio)
            print(f"You said: {text}")  # Debugging output

            if not text:
                continue

            # (3) Check for the wake word
            if "hey jarvis" in text.lower():
                print("Wake word detected. Listening for commands...")
                engine.say("I'm listening.")
                engine.runAndWait()

                time.sleep(2)  # Adding a delay to prepare for command

                # (4) Now listen for commands
                while True:
                    try:
                        print("Listening for command...")
                        command_audio = r.listen(source, timeout=30)  # Increased timeout for commands to 30 seconds
                        command = r.recognize_google(command_audio)
                        print(f"Command received: {command}")

                        # Check for exit phrase
                        if "thank you jarvis" in command.lower():
                            print("Exiting...")
                            engine.say("You're welcome! Goodbye.")
                            engine.runAndWait()
                            return  # Exit the function to stop listening

                        # Send input to OpenAI API using the updated syntax
                        response = client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": command}]
                        )
                        response_text = response.choices[0].message.content  # Updated content access
                        print(response_text)
                        print("Generating audio")

                        myobj = gTTS(text=response_text, lang=language, slow=False)
                        myobj.save("response.mp3")
                        print("Speaking")
                        os.system("cvlc response.mp3 --play-and-exit")

                        # Speak the response
                        engine.say(response_text)
                        engine.runAndWait()

                    except sr.UnknownValueError:
                        print("Could not understand the command. Please try again.")
                    except sr.RequestError as e:
                        print(f"Could not request results; {e}")
                        engine.say(f"Could not request results; {e}")
                        engine.runAndWait()
                        break

        except sr.UnknownValueError:
            print("No wake word detected. Please try again.")
            continue  # Continue listening for the wake word
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            engine.say(f"Could not request results; {e}")
            engine.runAndWait()
            break

# (5) Use the default microphone as the audio source
with sr.Microphone() as source:
    listen_and_respond(source)
