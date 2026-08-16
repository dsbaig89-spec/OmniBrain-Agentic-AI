from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from backend.app.services.pdf_agent import pdf_agent
from backend.app.services.image_agent import image_agent
from backend.app.services.csv_agent import csv_agent
from backend.app.services.chat_agent import chat_agent

from backend.app.services.langfuse_service import langfuse


# ==========================================
# State
# ==========================================

class AgentState(TypedDict):
    query: str
    agent: str
    answer: str


# ==========================================
# Router
# ==========================================

def route_query(state: AgentState):

    query = state["query"]
    q = query.lower().strip()

    # IMAGE
    if any(word in q for word in [
        "image",
        "picture",
        "photo",
        "diagram",
        "visual",
        "screenshot"
    ]):
        return {
            "agent": "image"
        }

    # CSV / DATA
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
        return {
            "agent": "csv"
        }

    # PDF / DOCUMENT
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
        return {
            "agent": "pdf"
        }

    # GENERAL CHAT
    else:
        return {
            "agent": "chat"
        }


# ==========================================
# Agent Nodes
# ==========================================

def pdf_node(state: AgentState):

    answer = pdf_agent(state["query"])

    return {
        "answer": answer
    }


def image_node(state: AgentState):

    answer = image_agent(state["query"])

    return {
        "answer": answer
    }


def csv_node(state: AgentState):

    answer = csv_agent(state["query"])

    return {
        "answer": answer
    }


def chat_node(state: AgentState):

    answer = chat_agent(state["query"])

    return {
        "answer": answer
    }


# ==========================================
# Conditional Routing
# ==========================================

def select_agent(state: AgentState):

    return state["agent"]


# ==========================================
# Build LangGraph
# ==========================================

builder = StateGraph(AgentState)

# Add nodes
builder.add_node("router", route_query)
builder.add_node("pdf_agent", pdf_node)
builder.add_node("image_agent", image_node)
builder.add_node("csv_agent", csv_node)
builder.add_node("chat_agent", chat_node)

# Start → Router
builder.add_edge(START, "router")

# Router → selected agent
builder.add_conditional_edges(
    "router",
    select_agent,
    {
        "pdf": "pdf_agent",
        "image": "image_agent",
        "csv": "csv_agent",
        "chat": "chat_agent",
    }
)

# Agents → End
builder.add_edge("pdf_agent", END)
builder.add_edge("image_agent", END)
builder.add_edge("csv_agent", END)
builder.add_edge("chat_agent", END)


# Compile graph
graph = builder.compile()


# ==========================================
# Public Supervisor Function
# ==========================================

def supervisor(query: str):

    with langfuse.start_as_current_observation(
        as_type="agent",
        name="omnibrain-langgraph-supervisor",
        input={
            "query": query
        }
    ) as trace:

        result = graph.invoke({
            "query": query,
            "agent": "",
            "answer": ""
        })

        trace.update(
            metadata={
                "selected_agent": result["agent"],
                "framework": "LangGraph"
            },
            output={
                "answer": result["answer"]
            }
        )

        return result["answer"]
    