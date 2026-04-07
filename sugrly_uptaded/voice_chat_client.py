import speech_recognition as sr
import requests
import os
import sys

# ==============================
# 🎙 Voice to Text Chat Client for Sugrly
# ==============================
# This script uses your local microphone for input and transcribes it
# using the language="ar-EG" setting. It then sends the text to the
# Sugrly AI via the /chat endpoint and prints the response.

BASE_URL = "http://127.0.0.1:8000"
TOKEN_ENDPOINT = f"{BASE_URL}/auth/token"
CHAT_ENDPOINT = f"{BASE_URL}/chat"

class SugrlyClient:
    def __init__(self):
        self.token = None
        self.recognizer = sr.Recognizer()

    def login(self):
        """Simple login flow to get JWT token from the FastAPI backend."""
        print("🔐 Welcome to Sugrly Voice Client")
        print("Please enter your credentials to connect to the AI Assistant.")
        email = input("Email (e.g. yassinahmed6109@gmail.com): ").strip()
        password = input("Password: ").strip()
        
        try:
            response = requests.post(
                TOKEN_ENDPOINT, 
                data={"username": email, "password": password},
                timeout=10
            )
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                print("✅ Login successful!")
                return True
            else:
                print(f"❌ Login failed ({response.status_code}): {response.text}")
                return False
        except Exception as e:
            print(f"❌ Connection error: Could not reach server at {BASE_URL}. Make sure 'uvicorn' is running.")
            return False

    def listen_and_transcribe(self):
        """Listens to the microphone and transcribes locally using Google STT (ar-EG)."""
        with sr.Microphone() as source:
            print("\n" + "-"*30)
            print("🎙 أنا بسمعك دلوقتي، اتفضل اتكلم... (قل 'خروج' للإنهاء)")
            # Ambient noise adjustment for better accuracy
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            try:
                # Same settings as your snippet
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                print("⏳ جاري معالجة الصوت...")
                # Using Arabic (Egypt) as requested
                text = self.recognizer.recognize_google(audio, language="ar-EG")
                return text
            except sr.WaitTimeoutError:
                return "⚠️ انتهى الوقت دون سماع صوت."
            except sr.UnknownValueError:
                return "⚠️ لم أفهم الكلام، حاول مرة أخرى."
            except sr.RequestError:
                return "⚠️ فشل الاتصال بخدمة Google STT (تأكد من وجود إنترنت)."
            except Exception as e:
                return f"⚠️ خطأ غير متوقع: {e}"

    def send_to_ai(self, text):
        """Send the transcribed text to the /chat endpoint."""
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            # chat endpoint in routers/chat.py expects a 'text' form field
            response = requests.post(CHAT_ENDPOINT, data={"text": text}, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json().get("response", "No response found.")
            else:
                return f"❌ Server Error ({response.status_code}): {response.text}"
        except Exception as e:
            return f"❌ Connection Error: {e}"

    def run(self):
        if not self.login():
            return

        print("\n🚀 Ready! Start speaking to Sugarly.")

        while True:
            text = self.listen_and_transcribe()
            
            # If nothing was transcribed or an error occurred
            if text.startswith("⚠️"):
                print(text)
                continue

            print(f"📝 أنت قلت: {text}")

            # Simple exit logic
            if any(k in text.lower() for k in ["خروج", "exit", "quit"]):
                print("🤖 مع السلامة!")
                break

            # Communication with AI
            print("🤖 Sugarly is thinking...")
            ai_response = self.send_to_ai(text)
            
            print("\n" + "═"*50)
            print(f"🤖 Sugarly Response:")
            print(ai_response)
            print("═"*50 + "\n")

if __name__ == "__main__":
    client = SugrlyClient()
    client.run()
