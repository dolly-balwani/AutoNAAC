import os
from typing import Dict, Any

from google import genai
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from state import AgentState

# Load environment variables
load_dotenv()

# --- Configuration ---
# Initialize the new Google GenAI Client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "gemini-2.5-flash-lite"

# Connect to the Vector Store (created in ingestion.py)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# --- Helper to call Gemini ---
def call_gemini(prompt: str) -> str:
    """Calls Gemini 1.5 Flash using the new google.genai SDK."""
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"[ERROR calling Gemini: {e}]"

# --- Nodes ---

def retrieve_node(state: AgentState):
    """Retriever Agent: Finds evidence for the criterion."""
    print(f"--- RETRIEVING EVIDENCE FOR: {state['criterion']} ---")

    docs = retriever.invoke(state["criterion"])
    evidence_text = "\n\n".join([f"Source ({d.metadata.get('source', 'Unknown')}): {d.page_content}" for d in docs])

    return {"evidence": evidence_text}

def writer_node(state: AgentState):
    """Writer Agent: Drafts the narrative based on evidence."""
    print("--- WRITING DRAFT ---")

    prompt = f"""
    You are an expert academic writer for NAAC Accreditation Reports.

    CRITERION: {state['criterion']}

    EVIDENCE:
    {state['evidence']}

    PREVIOUS CRITIQUE (if any):
    {state.get('critique', 'None')}

    TASK:
    Write a high-quality, professional narrative (approx 200 words) for this criterion.
    Use the evidence provided. If evidence mentions images, cite them as [Image: Description].
    Be factual and objective.
    """

    draft = call_gemini(prompt)
    return {"draft": draft, "revision_count": state.get("revision_count", 0) + 1}

def reviewer_node(state: AgentState):
    """Reviewer Agent: Checks the draft against standards."""
    print("--- REVIEWING DRAFT ---")

    prompt = f"""
    You are a strict NAAC Reviewer.

    CRITERION: {state['criterion']}
    DRAFT:
    {state['draft']}

    Check for:
    1. Relevance to the criterion.
    2. Use of provided evidence.
    3. Professional tone.

    If it is good, reply exactly with: APPROVE
    If it needs changes, provide brief feedback on what to fix.
    """

    critique = call_gemini(prompt)
    return {"critique": critique}

def router_node(state: AgentState):
    """Decides whether to loop back or finish."""
    critique = state.get("critique", "")
    count = state.get("revision_count", 0)

    if "APPROVE" in critique or count >= 3:
        print("--- DRAFT APPROVED (or max retries reached) ---")
        return "finalize"
    else:
        print("--- REJECTED, REVISING ---")
        return "revise"

# --- Graph Definition ---

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("retriever", retrieve_node)
workflow.add_node("writer", writer_node)
workflow.add_node("reviewer", reviewer_node)

# Add Edges
workflow.set_entry_point("retriever")
workflow.add_edge("retriever", "writer")
workflow.add_edge("writer", "reviewer")

# Conditional Edge
workflow.add_conditional_edges(
    "reviewer",
    router_node,
    {
        "finalize": END,
        "revise": "writer"
    }
)

app = workflow.compile()
