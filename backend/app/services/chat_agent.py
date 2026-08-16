from backend.app.services.vector_service import search_vectors
from backend.app.services.llm_service import generate_answer


def chat_agent(query: str):

    # Search uploaded documents
    results = search_vectors(query)

    context_parts = []

    for point in results:
        if point.payload and "text" in point.payload:
            context_parts.append(point.payload["text"])

    context = "\n\n".join(context_parts)

    # Generate answer using retrieved document context
    return generate_answer(query, context)