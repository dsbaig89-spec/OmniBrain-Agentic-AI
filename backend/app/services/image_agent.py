from backend.app.services.vector_service import search_vectors
from backend.app.services.llm_service import generate_answer


def image_agent(query: str):

    results = search_vectors(query)

    context_parts = []
    sources = []

    for point in results:

        if point.payload and "text" in point.payload:

            text = point.payload["text"]

            context_parts.append(text)

            sources.append({
                "text": text[:300]
            })

    context = "\n\n".join(context_parts)

    answer = generate_answer(query, context)

    return {
        "answer": answer,
        "sources": sources
    }