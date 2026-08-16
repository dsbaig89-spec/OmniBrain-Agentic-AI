from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.services.langgraph_supervisor import supervisor


router = APIRouter()


class SearchRequest(BaseModel):
    query: str


@router.post("/search", tags=["Search"])
def search(request: SearchRequest):

    answer = supervisor(request.query)

    return {
        "query": request.query,
        "answer": answer
    }