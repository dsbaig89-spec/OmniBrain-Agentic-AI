from backend.app.services.vector_service import search_vectors
from backend.app.services.llm_service import generate_answer


def csv_agent(query: str):

    results = search_vectors(query)

    context = ""

    for point in results:
        context += point.payload["text"] + "\n\n"

    return generate_answer(query, context)