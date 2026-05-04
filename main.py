# Standard Libraries
import webbrowser
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from dotenv import load_dotenv
# Third-Party Libraries
import speech_recognition as sr
# import pyttsx3
from gtts import gTTS
import pygame
# import vlc
from newsapi import NewsApiClient
from openai import OpenAI
import requests
import python_weather
import asyncio
import json
import time

load_dotenv()

# Web Browsing/Commands
class WebBrowsing:   
    def openPage(self, link):
        chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
        webbrowser.register('google-chrome', None, webbrowser.BackgroundBrowser(chrome_path))
        webbrowser.get('google-chrome')
        webbrowser.open(link, new=2)

# Basic System
class LocalFilesAndApps:
    def openFolder(self, link):
        try:
            os.startfile(link)
            return True
        except Exception:
            return False
    
    def openApp(self, link):
        try:
            os.startfile(link)
            return True
        except FileNotFoundError:
            print(f"Could not find '{link}'.")
            return False
        except Exception as e:
            print(f"Error opening '{link}': {e}")
            return False

# Data Retrieval 1      
class News:
    def __init__(self):
        my_secret_key = os.getenv("NEWS_API_KEY")
        self.api = NewsApiClient(api_key=my_secret_key)
    def readNews(self):
        headlines = self.api.get_top_headlines(language='en', country='in')
        
        if headlines['totalResults'] > 0:
            for article in headlines['articles']:
                print(f"TITLE: {article['title']}")
        else:
            print("No result. Trying global keywords. . .")
            alt_headlines = self.api.get_top_headlines(q='world')
            
            if alt_headlines.get('totalResults', 0) > 0 and len(alt_headlines.get('articles', [])) > 0:
                print(alt_headlines['articles'][0]['title'])
            else:
                print("Could not fetch any News headline right now. You may have reached your API limit.")

# Data Retrieval 2
class WeatherForecast:
    async def _fetch_weather(self, city):
        try:
            if not city:
                return "I need a valid city name to check the weather."
            
            async with python_weather.Client(unit=python_weather.METRIC) as client:
                
                weather = await client.get(city)

                report = f"The temperature for the city: {city} is {weather.temperature}°C.\nCondition: {weather.description}"
                print(report)
                return report
        except python_weather.errors.RequestError:
            return f"Sorry, I couldn't find any weather data for {city}"
        except Exception as e:
            print(f"Weather Fetch Error: {e}")
            return "There was an error fetching the weather."

    def readWeather(self, city):
        return asyncio.run(self._fetch_weather(city))

# Data Retrieval 3
class Wiki:
    def getSummary(self, title):
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        custom_header = {'User-Agent':'MyVoiceAssistantProject/1.0(your_email@example.com)'}
        summary = requests.get(url, headers=custom_header)
        
        if summary.status_code == 200:
            data = summary.json()
            extract = data['extract']
            print(f"The summary of the {title} is as below: ")
            print(extract)
        else:
            print(f"Error: {summary.status_code}")
            print(f"Reason: {summary.text}")

class CommandRouter:
    def __init__(self, weather_system, local_system):
        self.client = OpenAI(
            base_url="http://127.0.0.1:1234/v1",
            api_key="lm-studio"
        )
        self.weather_system = weather_system
        self.local_system = local_system
    def smartDecide(self, user_text):
        response = self.client.chat.completions.create(
            model="local-model",
            messages=[
                {"role":"system", "content":"You are a helpful Ai intelligent assistant. Your replies are creative and breif."},
                {"role":"user", "content": user_text}
            ],
            temperature=0.8
        )
        # print(f"Raw Response: {response}")
        ai_reply = response.choices[0].message.content
        print(f"Ai: {ai_reply}")

    def smartCalling(self, user_text):
        if not user_text:
            return "Sorry, I didn't catch that."
        response = self.client.chat.completions.create(
            model="local-model",
            messages=[
                {"role":"system", "content":"You are a helpful AI assistant. "
                        "You are a helpful AI assistant with access to tools. "
                        "RULE 1: If the user asks about the weather or temperature, you MUST use the get_weather tool. "
                        "RULE 2: If the user asks to open or launch an application, you MUST use the open_application tool. "
                        "RULE 3: For all other general conversation questions (like 'What is Python?'), answer directly in plain text without using any tools. "
                        "Do not explain your thought process. Just execute the rules."},
                {"role":"user", "content": user_text}
            ],
            tools=[ 
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Get current temperature for a given location.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "City or country. Example: Gandhinagar or Ahmedabad or India."
                                    }
                        },
                        "required": ["location"],
                        "additionalProperties": False
                        },
                        "strict": True  
                    }
                },

                {
                    "type": "function",
                    "function": {
                        "name": "open_application",
                        "description": "Opens a local application on the user's computer, such as a calculator.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "app_name": {
                                    "type": "string",
                                    "description": "The name of the application to open, it could be short names like 'calc' too and full name like 'calculator' or 'calculator app'. 'calculator' means 'calc'."
                                }
                            },
                            "required": ["app_name"],
                            "additionalProperties": False
                        },
                        "strict": True
                    }
                }
            ],
            tool_choice="auto",
            temperature=0.4
        )
        call = response.choices[0].message
        if call.tool_calls:
            tool= call.tool_calls[0]
            tool_name = tool.function.name
            tool_args_string = tool.function.arguments

            args_dict = json.loads(tool_args_string)
            if tool_name == "get_weather":

                city = args_dict.get("location", "").strip()
                if not city:
                    return "I'm sorry, but I didn't catch the city name. Which city's weather would you like to know?"
                
                return self.weather_system.readWeather(city)
            
            elif tool_name == "open_application":
                app_name = args_dict['app_name']
                success = self.local_system.openApp(app_name)
                if success:
                    return f"Opening {app_name} for you."
                else:
                    return f"Sorry, I couldn't find the application {app_name} on your system."
        
        else:
            print("No tool called, generating a random contextual response.")
            ai_reply = response.choices[0].message.content
            print(f"Ai: {ai_reply}")
            return ai_reply
        
class Listen:
    def __init__(self):
        self.r = sr.Recognizer()
    def userSpeaks(self):
        with sr.Microphone() as source:
            print("Calibrating for background noise. . .")
            self.r.adjust_for_ambient_noise(source, duration=1.0)
            print("Speak Now. . .")
            try:
                audio_data = self.r.listen(source, timeout=9, phrase_time_limit=15)
                text = self.r.recognize_google(audio_data)
                print("You said: " , text)
                return text
            
            except sr.UnknownValueError:
                print("Google speech recognition could not understand audio.")
                return None
            
            except sr.WaitTimeoutError:
                print("Listening timed out. No speech detected.")
                return None

# class Speak:
#     def __init__(self):
#         self.engine = pyttsx3.init()
#         rate = self.engine.getProperty('rate')
#         self.engine.setProperty('rate', rate - 30)
#         self.engine.setProperty('volume', 1)
#         voices = self.engine.getProperty('voices')
#         self.engine.setProperty('voice', voices[1].id)
#     def machineSpeaks(self, sentences):
#         self.engine.say(sentences)
#         self.engine.runAndWait()
#         self.engine.stop()
class Speak:
    def __init__(self):
        pygame.mixer.init()
    def machineSpeaks(self, sentences):
        if not sentences:
            return
        try:
            filename = f"response_{int(time.time())}.mp3"

            tts = gTTS(text=sentences, lang='en', slow=False)
            tts.save(filename)

            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

            time.sleep(0.2)

            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            pygame.mixer.music.unload()

            os.remove(filename)
        except Exception as e:
            print(f"Audio engine error: {e}")

# --- 1. CREATE THE OBJECTS ---
web_obj0 = WebBrowsing()
local_obj0 = LocalFilesAndApps()
news_obj0 = News()
weather_obj0 = WeatherForecast()
wiki_sum0 = Wiki()
command_obj0 = CommandRouter(weather_obj0, local_obj0)
listen_obj0 = Listen()
speak_obj0 = Speak()

# --- 2. ONE-OFF TESTS / STARTUP COMMANDS (Keep these commented unless testing) ---
# web_obj0.openPage("https://www.youtube.com/")
# local_obj0.openFolder("D:/Yash Everything Folder/Anime/Alya Sometimes Hides Her Feelings in Russian/(Alya Sometimes Hides Her Feelings in Russian) (Season 01) [BD 1080p][HEVC x265 10bit][Dual-Audio][Eng-Subs]/Season 01/[Judas] Roshidere -S01E01.mkv")
# local_obj0.openApp("C:/Windows/System32/calc.exe")
# news_obj0.readNews()
# print("-------------------")
# weather_obj0.readWeather("Gandhinagar")
# print("-------------------")
# wiki_sum0.getSummary("India")
# print("-------------------")
# command_obj0.smartDecide("Can I take pyhton to go in could computing, cybersecurity, data science, ai/ml? Give me the priority order")
# print("-------------------")
# command_obj0.smartCalling("What is India?")
# print("-------------------")
# command_obj0.smartCalling("What is the current weather in Gandhinagar?")
# print("-------------------")
# command_obj0.smartCalling("Open calc app.")
# listen_obj0.userSpeaks()
# command_obj0.smartCalling(listen_obj0.userSpeaks())

# --- 3. THE INFINITE LOOP ---
while True:
    print("--------Alya is listening--------")
    user_input = listen_obj0.userSpeaks()
    if user_input is None:
        continue
    ai_response = command_obj0.smartCalling(user_input)
    if ai_response:
        speak_obj0.machineSpeaks(ai_response)
