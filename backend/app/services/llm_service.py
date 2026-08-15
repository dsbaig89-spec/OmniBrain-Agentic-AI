from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables from backend/.env
load_dotenv("backend/.env")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_answer(question, context):

    prompt = f"""
You are an AI assistant.

Answer the user's question using ONLY the context below.

Context:
{context}

Question:
{question}

If the answer is not in the context, say:
'I couldn't find the answer in the uploaded documents.'
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content