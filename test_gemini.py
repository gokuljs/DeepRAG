import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
MODEL = 'gemini-2.5-flash'

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY environment variable not set")
client = genai.Client(api_key=api_key)

def generate_content():
    prompt = "why is the sky blue?"
    response = client.models.generate_content(
        model=MODEL, contents=prompt
    )
    print(response.text[:1000])
    print(response.usage)

if __name__ == "__main__":
    generate_content()