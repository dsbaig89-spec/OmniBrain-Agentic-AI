from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.services.vector_service import search_vectors
from backend.app.services.llm_service import generate_answer

router = APIRouter()


class SearchRequest(BaseModel):
    query: str


@router.post("/search", tags=["Search"])
def search(request: SearchRequest):

    results = search_vectors(request.query)

    context = ""

    for point in results:
        context += point.payload["text"] + "\n\n"

    answer = generate_answer(
        request.query,
        context
    )

    return {
        "query": request.query,
        "answer": answer
    }