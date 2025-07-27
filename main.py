import speech_recognition as sr
import webbrowser
import pygame
from gtts import gTTS
import os
import musicLibrary
from datetime import datetime
import requests


# Initialize Pygame mixer ONCE
pygame.mixer.init()

recognizer = sr.Recognizer()

def speak(text):
    try:
        tts = gTTS(text=text, lang='en')
        tts.save('temp.mp3')
        
        pygame.mixer.music.load('temp.mp3')
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        # Stop and unload the music to release the file
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()  # Critical for file release
        
    except Exception as e:
        print(f"Error in speak(): {e}")
    finally:
        # Small delay to ensure file release (optional)
        pygame.time.delay(100)  
        if os.path.exists('temp.mp3'):
            try:
                os.remove('temp.mp3')
            except PermissionError:
                print("Failed to delete temp.mp3 (still locked)")

def process_command(command):
    command = command.lower()
    if "open google" in command:
        webbrowser.open("https://www.google.com")
        speak("Opening Google")
    elif "open facebook" in command:
        webbrowser.open("https://www.facebook.com")
        speak("Opening Facebook")
    elif "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube")
    elif "open instagram" in command:
        webbrowser.open("https://www.instagram.com")
        speak("Opening Instagram")
    elif "open stackoverflow" in command:
        webbrowser.open("https://www.stackoverflow.com")
     #  Time Command
    elif "what time is it" in command or "current time" in command:
        current_time = datetime.now().strftime("%I:%M %p")  # Example: "03:45 PM"
        speak(f"The current time is {current_time}")
    
    #  Date Command
    elif "what day is it" in command or "today's date" in command:
        current_date = datetime.now().strftime("%A, %B %d, %Y")  # Example: "Monday, July 05, 2025"
        speak(f"Today is {current_date}")
    elif "calculate" in command or "what is" in command:
        try:
        # Extract expression
            expr = command.split("calculate")[1] if "calculate" in command else command.split("what is")[1]
            expr = expr.strip()
            
            # Convert words to symbols
            expr = (expr.replace("plus", "+")
                    .replace("minus", "-")
                    .replace("times", "*")
                    .replace("x", "*")
                    .replace("divided by", "/")
                    .replace("percent", "*0.01")
                    .replace("squared", "**2"))
            
            # Calculate safely
            result = eval(expr)  # For prototyping (or use `ast.literal_eval` for safety)
            
            # Speak result
            if result.is_integer():
                speak(f"The result is {int(result)}")
            else:
                speak(f"The result is {round(result, 2)}")
            
        except ZeroDivisionError:
            speak("You can't divide by zero!")
        except:
            speak("Sorry, I couldn't calculate that. Try saying 'Calculate 5 plus 3'.")
    elif "weather" in command:
        try:
            # Set Islamabad as default city
            city = "Islamabad"  # Changed from  "Islamabad"
            
            # Check if user specified a different city
            if "in" in command:
                city = command.split("in")[1].strip()
            
            # API Call 
            api_key = "1b927d523b628a7ef8f3a09777127cfe"  
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url)
            weather_data = response.json()
            
            # Error handling if city not found
            if weather_data.get("cod") != 200:
                speak(f"Sorry, I couldn't find weather for {city}.")
                return
            
            # Extract weather details
            temp = weather_data['main']['temp']
            desc = weather_data['weather'][0]['description']
            humidity = weather_data['main']['humidity']
            
            # Speak the weather report
            speak(f"Weather in {city}: {desc}, Temperature: {temp}°C, Humidity: {humidity}%")
        
        except Exception as e:
            print(f"Error fetching weather: {e}")
            speak("Sorry, I couldn't check the weather right now.")
    elif command.startswith("play"):
        try:
            # Extract the full song name after "play"
            song_name = ' '.join(command.split()[1:]).lower()  # Gets everything after "play" and makes lowercase
            
            # Find matching song (case-insensitive)
            matching_song = None
            for song in musicLibrary.music:
                if song.lower() == song_name:
                    matching_song = song
                    break
            
            if matching_song:
                link = musicLibrary.music[matching_song]
                webbrowser.open(link)
                speak(f"Playing {matching_song}")
            else:
                # Suggest similar songs if not found
                suggestions = [s for s in musicLibrary.music if song_name in s.lower()]
                if suggestions:
                    speak(f"Song not found. Did you mean: {', '.join(suggestions)}?")
                else:
                    speak("Song not found in library. Available songs are: " + ", ".join(musicLibrary.music.keys()))
                    
        except IndexError:
            speak("Please specify a song name.")
        except Exception as e:
            speak(f"Error playing music: {e}")
    elif "goodbye" in command or "exit" in command:
        speak("Goodbye! Have a great day!")
        exit()
    else:
        speak("I didn't understand that command. Please try again.")

if __name__ == "__main__":
    speak("Hy,this is Alexa,how can i assisit you Today? ")
    
    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for wake word...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
            
            wake_word = recognizer.recognize_google(audio).lower()
            print(f"Recognized: {wake_word}")
            
            if "alexa" in wake_word:
                speak("Yes?")
                print("Alexa Active...")

                with sr.Microphone() as source:
                    print("Listening for command...")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    command = recognizer.recognize_google(audio).lower()
                    print(f"Command: {command}")
                    process_command(command)
        
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except Exception as e:
            print(f"Error: {e}")