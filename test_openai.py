import openai
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import os
from dotenv import load_dotenv

load_dotenv()

# Use the environment variable for API key or set it directly

try:
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
    ])
    print(response.choices[0].message.content)
except openai.AuthenticationError:
    print("Invalid API key. Please check it.")
except Exception as e:
    print(f"An error occurred: {e}")
