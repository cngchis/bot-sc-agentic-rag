import json
from langchain_core.documents import Document
from src.vectorstore.pinecone_store import get_vectorstore
from src.utils.helper import get_env

def ingest_json():
    json_dir = get_env("JSON_DIR")

    with open(json_dir, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} records from {json_dir}")

    docs = []
    for idx, item in enumerate(data):
        query = item.get("query", "")
        answer = item.get("reference", "")

        content = f"Question: {query}\nAnswer: {answer}"

        docs.append(Document(
            page_content=content,
            metadata={
                "source": json_dir,
                "row": idx,
                "query": query
            }
        ))

    vectorstore = get_vectorstore()
    vectorstore.add_documents(docs)

    print(f"Ingested {len(docs)} documents into Pinecone")

if __name__ == "__main__":
    ingest_json()