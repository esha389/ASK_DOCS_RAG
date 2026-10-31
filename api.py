"""
Backend for the RAG project. A custom web page (in the `web` folder) talks to this.
It reuses YOUR code from src/ (FaissVectorStore and RAGSearch).

Run from the RAG folder:
    uvicorn api:app --reload
Then open http://127.0.0.1:8000
"""
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.search import RAGSearch
from src.vectorstore import FaissVectorStore

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------------
# Load once when the server starts (same calls as your old app.py)
# ---------------------------------------------------------------
rag = RAGSearch()

store = getattr(rag, "vectorstore", None)
if store is None:
    store = FaissVectorStore("faiss_store")
    store.load()

app = FastAPI(title="RAG API")


class AskRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


def get_sources(query: str, top_k: int):
    """Ask the vector store for the closest chunks, for the 'Sources' part of the page."""
    sources = []
    try:
        results = store.query(query, top_k=top_k)
        for r in results:
            meta = (r.get("metadata") or {}) if isinstance(r, dict) else {}
            page = meta.get("page")
            file_name = meta.get("source_file") or Path(str(meta.get("source", ""))).name or None
            distance = r.get("distance") if isinstance(r, dict) else None
            sources.append(
                {
                    "file": file_name,
                    "page": page + 1 if isinstance(page, int) else None,
                    "distance": round(float(distance), 3) if distance is not None else None,
                    "text": meta.get("text") or meta.get("content") or "",
                }
            )
    except Exception as e:
        print(f"[WARN] Could not build sources: {e}")
    return sources


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/ask")
def ask(req: AskRequest):
    try:
        answer = rag.search_and_summarize(req.query, top_k=req.top_k)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"RAG error: {e}")

    return {"answer": answer, "sources": get_sources(req.query, req.top_k)}


# Serve the custom frontend from the `web` folder (must be added LAST)
WEB_DIR = BASE_DIR / "web"
if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")