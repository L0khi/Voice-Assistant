import pyttsx3
import speech_recognition as sr
import yt_dlp
import webbrowser
import time
import requests
import PyPDF2
import yfinance as yf
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
import re

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

def speak_response(response):
    if response:
        print("Assistant:", response)
        engine.say(response)
        engine.runAndWait()

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print("You:", command)
            return command.lower()
        except:
            speak_response("Sorry, I didn't catch that.")
            return ""

def play_music(command):
    song = command.replace("play music", "").strip()
    if not song:
        speak_response("Which song?")
        song = listen_for_command()
    ydl_opts = {'quiet': True, 'extract_flat': True, 'force_generic_extractor': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch:{song}", download=False)
        if 'entries' in result:
            video = result['entries'][0]
            webbrowser.open(video['url'])
            return f"Playing: {video['title']}"
        else:
            return "Couldn't find the song."

def get_weather():
    api_key = "your_openweathermap_api_key"
    city = "Toronto"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        res = requests.get(url).json()
        if res["cod"] != 200:
            return f"Weather fetch failed: {res.get('message')}"
        desc = res['weather'][0]['description']
        temp = res['main']['temp']
        return f"The weather in {city} is {desc} with {temp}°C."
    except Exception as e:
        return f"Error: {e}"

def get_news():
    api_key = "your_news_api_key"
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    try:
        res = requests.get(url).json()
        headlines = [a['title'] for a in res['articles'][:5]]
        return "Top headlines: " + "; ".join(headlines)
    except Exception as e:
        return f"News error: {e}"

def get_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d")
        if hist.empty:
            return "No stock data found."
        price = hist['Close'].iloc[-1]
        return f"{symbol.upper()} is trading at ${price:.2f}"
    except:
        return "Stock fetch error."

def read_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''.join([page.extract_text() for page in reader.pages])
        speak_response(text[:1000])
        return "Done reading PDF."
    except Exception as e:
        return f"PDF error: {e}"

def read_webpage(url):
    try:
        html = urllib.request.urlopen(url)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        speak_response(text[:1000])
        return "Done reading web content."
    except:
        return "Webpage read failed."

def set_timer(command):
    match = re.search(r"(\d+)", command)
    if not match:
        return "Please specify minutes for the timer."
    minutes = int(match.group(1))
    speak_response(f"Timer set for {minutes} minutes.")
    time.sleep(minutes * 60)
    return f"{minutes} minutes timer ended."

def get_date_time():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"The current date and time is {now}"

def main():
    speak_response("Assistant is ready.")
    while True:
        command = listen_for_command()
        if not command:
            continue
        if "stop" in command or "exit" in command:
            speak_response("Goodbye.")
            break
        elif "play music" in command:
            speak_response(play_music(command))
        elif "weather" in command:
            speak_response("will get the weather for you in next update with api subscription. thanks for your patience.")
        elif "news" in command:
            speak_response(get_news())
        elif "stock" in command:
            symbol = command.replace("stock", "").strip().upper()
            speak_response(get_stock_price(symbol))
        elif "read pdf" in command:
            path = command.replace("read pdf", "").strip()
            speak_response(read_pdf(path))
        elif "read webpage" in command:
            url = command.replace("read webpage", "").strip()
            speak_response(read_webpage(url))
        elif "set timer" in command:
            speak_response(set_timer(command))
        elif "time" in command or "date" in command:
            speak_response(get_date_time())
        else:
            speak_response("Command not recognized.")

if __name__ == "__main__":
    main()
