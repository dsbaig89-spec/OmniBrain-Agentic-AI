from backend.app.services.pdf_agent import pdf_agent
from backend.app.services.image_agent import image_agent
from backend.app.services.csv_agent import csv_agent
from backend.app.services.chat_agent import chat_agent


def supervisor(query: str):

    q = query.lower()

    if any(word in q for word in [
        "pdf",
        "document",
        "page",
        "chapter",
        "report"
    ]):
        return pdf_agent(query)

    elif any(word in q for word in [
        "image",
        "picture",
        "photo",
        "diagram",
        "graph"
    ]):
        return image_agent(query)

    elif any(word in q for word in [
        "csv",
        "table",
        "column",
        "row",
        "dataset",
        "data"
    ]):
        return csv_agent(query)

    else:
        return chat_agent(query)