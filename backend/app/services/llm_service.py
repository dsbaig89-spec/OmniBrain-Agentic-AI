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
You are an AI assistant.

Answer the user's question using ONLY the context below.

Context:
{context}

Question:
{question}

If the answer is not in the context, say:
'I couldn't find the answer in the uploaded documents.'
"""

    # Create Langfuse trace/span
    with langfuse.start_as_current_observation(
        as_type="span",
        name="omnibrain-rag"
    ) as span:

        span.update(
            input={
                "question": question
            }
        )

        # Track the LLM generation
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

    # Send trace data to Langfuse
    langfuse.flush()

    return answer