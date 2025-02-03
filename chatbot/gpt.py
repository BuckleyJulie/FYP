import openai
import os
from dotenv import load_dotenv

load_dotenv()

# Use the environment variable for API key or set it directly
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_script_response(user_input, conversation):
    """Sends user input to OpenAI and returns the assistant's response."""
    conversation.append({"role": "user", "content": user_input})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation
        )

        reply = response['choices'][0]['message']['content']
        conversation.append({"role": "assistant", "content": reply})
        
        return reply, 
    except Exception as e:
        return f"An error occurred: {e}"
