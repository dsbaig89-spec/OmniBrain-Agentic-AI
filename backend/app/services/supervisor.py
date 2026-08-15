from backend.app.services.pdf_agent import pdf_agent
from backend.app.services.image_agent import image_agent
from backend.app.services.csv_agent import csv_agent
from backend.app.services.chat_agent import chat_agent


def supervisor(query: str):

    q = query.lower().strip()

    # ==========================================
    # IMAGE QUESTIONS
    # ==========================================
    if any(word in q for word in [
        "image",
        "picture",
        "photo",
        "diagram",
        "visual",
        "screenshot"
    ]):
        return image_agent(query)


    # ==========================================
    # CSV / DATA QUESTIONS
    # ==========================================
    elif any(word in q for word in [
        "csv",
        "table",
        "column",
        "row",
        "dataset",
        "data",
        "average",
        "total",
        "maximum",
        "minimum"
    ]):
        return csv_agent(query)


    # ==========================================
    # PDF / UPLOADED FILE QUESTIONS
    # ==========================================
    elif any(word in q for word in [
        "pdf",
        "file",
        "uploaded",
        "upload",
        "document",
        "page",
        "chapter",
        "report",
        "resume",
        "cv",
        "name",
        "education",
        "degree",
        "college",
        "university",
        "qualification",
        "experience",
        "project",
        "skill",
        "skills",
        "father",
        "mother",
        "nationality",
        "date of birth",
        "dob",
        "phone",
        "email",
        "career",
        "objective",
        "certification",
        "certificate",
        "about",
        "belongs",
        "owner"
    ]):
        return pdf_agent(query)


    # ==========================================
    # DEFAULT
    # ==========================================
    else:
        return chat_agent(query)