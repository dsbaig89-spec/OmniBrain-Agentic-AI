from backend.app.services.llm_service import generate_answer


def chat_agent(query: str):
    return generate_answer(query, "")