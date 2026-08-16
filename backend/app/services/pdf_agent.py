from backend.app.services.vector_service import search_vectors
from backend.app.services.llm_service import generate_answer
from backend.app.services.langfuse_service import langfuse


def pdf_agent(query: str):

    # Trace the retrieval step
    with langfuse.start_as_current_observation(
        as_type="span",
        name="qdrant-retrieval"
    ) as retrieval:

        retrieval.update(
            input={
                "query": query
            }
        )

        # Search Qdrant
        results = search_vectors(query)

        # Collect retrieved chunks
        context_parts = []

        for point in results:
            if point.payload and "text" in point.payload:
                context_parts.append(point.payload["text"])

        context = "\n\n".join(context_parts)

        # Record retrieved information
        retrieval.update(
            output={
                "chunks_retrieved": len(context_parts),
                "context": context
            }
        )

    # Generate final answer using retrieved context
    answer = generate_answer(query, context)

    # Send trace data to Langfuse
    langfuse.flush()

    return answer