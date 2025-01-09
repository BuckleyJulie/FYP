import openai
import os
from dotenv import load_dotenv

load_dotenv()

# Use the environment variable for API key or set it directly
openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"},
        ]
    )
    print(response['choices'][0]['message']['content'])
except openai.error.AuthenticationError:
    print("Invalid API key. Please check it.")
except Exception as e:
    print(f"An error occurred: {e}")
