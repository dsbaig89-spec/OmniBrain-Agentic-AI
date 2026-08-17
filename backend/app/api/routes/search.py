from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.services.langgraph_supervisor import supervisor

router = APIRouter()


class SearchRequest(BaseModel):
    query: str


@router.post("/search", tags=["Search"])
def search(request: SearchRequest):

    result = supervisor(request.query)

    # If an agent returns a dictionary
    if isinstance(result, dict):

        return {
            "query": request.query,
            "answer": result.get("answer", ""),
            "sources": result.get("sources", [])
        }

    # If an agent returns a plain string
    return {
        "query": request.query,
        "answer": str(result),
        "sources": []
    }