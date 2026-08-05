from fastapi import FastAPI
from backend.app.api.router import api_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="OmniBrain Agentic AI",
    version="1.0.0",
    description="Enterprise Agentic AI Search Platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to OmniBrain Agentic AI 🚀"
    }