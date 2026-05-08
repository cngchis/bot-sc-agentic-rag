import os
import torch
from dotenv import load_dotenv
from openai import OpenAI
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

def get_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise ValueError(f"Missing env variable: {key}")
    return val

def format_docs(docs: list) -> str:
    return "\n\n".join(d.page_content for d in docs)

def log_node(name: str, state: dict):
    print(f"[NODE] {name}")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL_NAME = "gpt-4o-mini"

_sessions: dict[str, list] = {}

def _invoke_with_fallback(messages) -> str:
    formatted = []

    for m in messages:
        if isinstance(m, HumanMessage):
            role = "user"
        else:
            role = "assistant"

        formatted.append({
            "role": role,
            "content": m.content
        })

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=formatted,
        temperature=0.2,
    )

    return response.choices[0].message.content
    
def get_session_history(session_id: str) -> list:
    if session_id not in _sessions:
        _sessions[session_id] = []
    return _sessions[session_id]
    
def get_llm_response(prompt: str, query: str = None, session_id: str = "default") -> str:
    history = get_session_history(session_id)
    messages = [*history, HumanMessage(content=prompt)]
    answer = _invoke_with_fallback(messages)

    history_key = query if query else prompt
    history.append(HumanMessage(content=history_key))
    history.append(AIMessage(content=answer))

    return answer

def reset_session(session_id: str):
    if session_id in _sessions:
        del _sessions[session_id]
        print(f"Reset session: {session_id}")

def reset_all_sessions():
    _sessions.clear()