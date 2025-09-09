import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env (make sure it has OPENAI_API_KEY=sk-xxxxxxx)
load_dotenv()

client = OpenAI()

try:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello, just to confirm my API key works."},
        ],
    )
    print("✅ Success! API key works.")
    print("Model reply:", resp.choices[0].message.content.strip())
except Exception as e:
    print("❌ Something went wrong:", e)

