import os

from dotenv import load_dotenv
from groq import Groq

from backend.app.services.vector_service import search_vectors

load_dotenv("backend/.env")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL = "openai/gpt-oss-20b"


def build_context(results):

    context = ""

    for point in results:

        if point.payload and "text" in point.payload:

            context += point.payload["text"]
            context += "\n\n"

    return context


def is_relevant(question, context):

    if not context.strip():
        return False

    prompt = f"""
Determine whether the retrieved context is relevant to the question.

Question:
{question}

Context:
{context}

Answer ONLY:
YES
or
NO
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
    )

    return response.choices[0].message.content.strip().upper().startswith("YES")


def rewrite_query(question):

    prompt = f"""
Rewrite the following question into a better semantic-search query.

Original question:
{question}

Return ONLY the rewritten query.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
    )

    return response.choices[0].message.content.strip()


def retrieve_with_self_correction(question):

    # First attempt
    results = search_vectors(question)

    context = build_context(results)

    if is_relevant(question, context):

        return results

    # Self-correction
    rewritten = rewrite_query(question)

    print(
        f"[SELF-RAG] Rewriting query: "
        f"{question} -> {rewritten}"
    )

    results = search_vectors(rewritten)

    return results