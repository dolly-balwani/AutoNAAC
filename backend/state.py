from typing import TypedDict, List, Annotated
import operator

class AgentState(TypedDict):
    """
    Represents the state of the NAAC Report Generation process.
    """
    criterion: str          # e.g., "1.1.1 Curricular Planning"
    evidence: str           # Retrieved text snippets from ChromaDB
    draft: str              # The current narrative draft
    critique: str           # Feedback from the Reviewer
    revision_count: int     # To prevent infinite loops (max retries)
    final_report: str       # The approved text
