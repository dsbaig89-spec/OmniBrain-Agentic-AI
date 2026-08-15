from backend.app.services.pdf_agent import pdf_agent
from backend.app.services.image_agent import image_agent
from backend.app.services.csv_agent import csv_agent
from backend.app.services.chat_agent import chat_agent

from backend.app.services.langfuse_service import langfuse


def supervisor(query: str):

    q = query.lower().strip()

    # Start Langfuse trace
    with langfuse.start_as_current_observation(
        as_type="agent",
        name="omnibrain-supervisor",
        input={"query": query},
    ) as trace:

        # ==========================================
        # IMAGE
        # ==========================================

        if any(word in q for word in [
            "image",
            "picture",
            "photo",
            "diagram",
            "visual",
            "screenshot"
        ]):

            agent = "image_agent"
            trace.update(metadata={"selected_agent": agent})

            answer = image_agent(query)

        # ==========================================
        # CSV / DATA
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

            agent = "csv_agent"
            trace.update(metadata={"selected_agent": agent})

            answer = csv_agent(query)

        # ==========================================
        # PDF / DOCUMENT
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

            agent = "pdf_agent"
            trace.update(metadata={"selected_agent": agent})

            answer = pdf_agent(query)

        # ==========================================
        # GENERAL CHAT
        # ==========================================

        else:

            agent = "chat_agent"
            trace.update(metadata={"selected_agent": agent})

            answer = chat_agent(query)

        # Store final answer in trace
        trace.update(
            output={
                "answer": answer
            }
        )

        return answer