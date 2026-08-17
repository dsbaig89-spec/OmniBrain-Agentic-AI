from groq import Groq
from dotenv import load_dotenv
from langfuse import get_client
import os

load_dotenv("backend/.env")

# Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Langfuse client
langfuse = get_client()


def generate_answer(question, context):
    
    prompt = f"""
You are OmniBrain, an AI assistant that answers questions using uploaded documents.

Use the retrieved context below to answer the user's question.

IMPORTANT RULES:
1. Use the information present in the context.
2. If the answer is clearly present, answer directly.
3. Do not say "I couldn't find the answer" when the context contains the answer.
4. Do not invent information that is not present.
5. Keep the answer concise.
6. For personal/profile questions, extract the exact information from the context.

Retrieved Context:
{context}

User Question:
{question}

Answer:
"""

    with langfuse.start_as_current_observation(
        as_type="span",
        name="omnibrain-rag"
    ) as span:

        span.update(
            input={
                "question": question,
                "context": context
            }
        )

        with langfuse.start_as_current_observation(
            as_type="generation",
            name="groq-generation",
            model="llama-3.3-70b-versatile"
        ) as generation:

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

            answer = response.choices[0].message.content

            generation.update(
                input=prompt,
                output=answer
            )

        span.update(
            output={
                "answer": answer
            }
        )

    langfuse.flush()

    return answer