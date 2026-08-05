from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "success",
        "message": "OmniBrain Agentic AI Backend is running successfully 🚀"
    }