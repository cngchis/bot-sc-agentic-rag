from typing import TypedDict

class GraphState(TypedDict):
    query           : str
    context         : str
    source          : str
    score           : float
    is_relevant     : str
    augmented_prompt: str
    answer          : str
    session_id      : str