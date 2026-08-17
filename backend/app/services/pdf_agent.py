from backend.app.services.self_rag_service import (
    retrieve_with_self_correction
)

from backend.app.services.llm_service import generate_answer
from backend.app.services.langfuse_service import langfuse


def pdf_agent(query: str):

    # ==========================================
    # Self-RAG + Qdrant Retrieval
    # ==========================================

    with langfuse.start_as_current_observation(
        as_type="span",
        name="qdrant-retrieval"
    ) as retrieval:

        retrieval.update(
            input={
                "query": query
            }
        )

        # Self-RAG retrieval
        results = retrieve_with_self_correction(query)

        context_parts = []
        sources = []
        seen_text = set()

        # ==========================================
        # Process Retrieved Results
        # ==========================================

        for point in results:

            if point.payload and "text" in point.payload:

                text = point.payload["text"].strip()

                # Skip duplicate chunks
                if text in seen_text:
                    continue

                seen_text.add(text)

                context_parts.append(text)

                source = {
                    "text": text[:300]
                }

                # Preserve PDF page information
                if "page" in point.payload:
                    source["page"] = point.payload["page"]

                if "filename" in point.payload:
                    source["filename"] = point.payload["filename"]

                sources.append(source)

        context = "\n\n".join(context_parts)

        # ==========================================
        # Langfuse Retrieval Observation
        # ==========================================

        retrieval.update(
            output={
                "chunks_retrieved": len(context_parts),
                "context": context
            }
        )

    # ==========================================
    # Generate Final Answer
    # ==========================================

    answer = generate_answer(
        query,
        context
    )

    # ==========================================
    # Flush Langfuse
    # ==========================================

    langfuse.flush()

    # ==========================================
    # Return Answer + Sources
    # ==========================================

    return {
        "answer": answer,
        "sources": sources
    }