# 🎙️ Alya: Local AI Voice Assistant

> Developed a modular, voice-activated AI assistant in Python. Integrated a local LLM with JSON tool-calling to autonomously fetch weather, summarize news, and launch local applications. Engineered a robust asynchronous event loop with speech recognition and Google text-to-speech for seamless, continuous voice interaction.

---

## ✨ Key Features

* **Privacy-First Local AI:** Powered by a local **Llama 3.1** model via LM Studio, ensuring zero data leakage for conversational queries.
* **Autonomous Tool-Calling:** The AI intelligently routes user intent into executable Python methods using JSON function-calling.
* **Real-Time Data Integration:** 
  * 🌤️ **Weather:** Live, asynchronous meteorological data via `python-weather`.
  * 📰 **News:** Top national and global headlines via RESTful calls to `NewsAPI`.
  * 🌐 **Wikipedia:** Instant contextual summaries using the public Wikipedia API.
  * 💻 **System Control:** Ability to locate and launch local executable files and applications.
* **Low-Latency Audio Engine:** Custom-built playback system utilizing `gTTS` and `pygame` to prevent Windows audio-thread deadlocks and ensure continuous conversation loops.

---

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **AI/LLM Integration:** OpenAI Python Client (routed to local LM Studio server)
* **Voice & Audio:** `SpeechRecognition`, `gTTS`, `pygame`, `PyAudio`
* **APIs & Networking:** `requests`, `python-weather`, `newsapi-python`
* **Architecture:** Object-Oriented Programming (OOP), Asynchronous I/O (`asyncio`)

---

## 🚀 Getting Started

### Prerequisites
1. **Python 3.8+** installed on your system.
2. A working microphone.
3. **LM Studio** installed and running on your local machine with a Llama 3.1 model loaded. 
   *(Ensure the local inference server is started on `http://127.0.0.1:1234`)*.

### Installation & Setup

**1. Install Dependencies**  
Navigate to the project folder in your terminal and install the required libraries:
```bash
pip install -r requirements.txt
```

**2. Configure Environment Variables**  
This project requires a free API key from [NewsAPI](https://newsapi.org/) to fetch current headlines. 
* Rename the `.env.example` file to `.env`.
* Open `.env` and paste your API key:
```text
NEWS_API_KEY="your_actual_key_here"
```
*(Note: Wikipedia API calls use a standard `example.com` placeholder in the codebase to protect personal contact information when hosting publicly.)*

**3. Run the Assistant**  
Start the main script to initialize Alya. The system will calibrate to your background noise and await your voice commands.
```bash
python main.py
```

---

## 🧠 System Architecture

The project is structured into modular, object-oriented classes for easy scaling:
* `Listen` / `Speak`: Handles the speech-to-text and text-to-speech event loop.
* `CommandRouter`: The core AI brain that receives text, prompts the local LLM, and triggers tools.
* `WeatherForecast`: Asynchronous API handler for `wttr.in`.
* `News` / `Wiki`: Synchronous REST API handlers.
* `LocalFilesAndApps`: OS-level execution manager.

---

## 👤 Author
**Yash Raval**  
AI Backend Engineer | Python Developer
