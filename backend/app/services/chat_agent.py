from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv("backend/.env")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def chat_agent(query: str):

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": """
You are OmniBrain, a helpful AI assistant.

For general conversation, answer naturally and helpfully.

Do not say that you need uploaded documents for normal greetings,
casual conversation, or general questions.
"""
            },
            {
                "role": "user",
                "content": query
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content