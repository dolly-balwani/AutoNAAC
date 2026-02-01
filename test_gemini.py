import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def test_raw_multi():
    models = [
        "models/gemini-1.5-flash", 
        "gemini-1.5-flash",
        "models/gemini-1.5-flash-001",
        "models/gemini-pro",
        "gemini-pro"
    ]
    
    for m in models:
        print(f"Testing {m}...")
        try:
            model = genai.GenerativeModel(m)
            response = model.generate_content("Hello")
            print(f"✅ SUCCESS with {m}! Response: {response.text}")
            return
        except Exception as e:
            print(f"❌ FAILED {m}. Error: {e}")

if __name__ == "__main__":
    test_raw_multi()
