from backend.app.services.vector_service import search_vectors
from backend.app.services.llm_service import generate_answer
from backend.app.services.langfuse_service import langfuse


def pdf_agent(query: str):

    with langfuse.start_as_current_observation(
        as_type="span",
        name="qdrant-retrieval"
    ) as retrieval:

        retrieval.update(
            input={
                "query": query
            }
        )

        results = search_vectors(query)

        context_parts = []
        sources = []
        seen_text = set()

        for point in results:

            if point.payload and "text" in point.payload:

                text = point.payload["text"].strip()

                # Remove duplicate chunks
                if text in seen_text:
                    continue

                seen_text.add(text)

                context_parts.append(text)

                sources.append({
                    "text": text[:300]
                })

        context = "\n\n".join(context_parts)

        retrieval.update(
            output={
                "chunks_retrieved": len(context_parts),
                "context": context
            }
        )

    answer = generate_answer(query, context)

    langfuse.flush()

    return {
        "answer": answer,
        "sources": sources
    }