import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

models_to_try = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-001",
    "gemini-flash-latest",
    "gemini-1.5-flash",
    "gemini-pro-latest"
]

for m in models_to_try:
    print(f"Testing '{m}'...")
    try:
        response = client.models.generate_content(model=m, contents="Hi")
        print(f"✅ SUCCESS with '{m}'! Response: {response.text[:50]}")
        break
    except Exception as e:
        print(f"❌ FAILED: {e}")
