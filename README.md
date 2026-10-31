# Ask Docs RAG

A lightweight retrieval-augmented generation app for asking questions about local documents and reading answers with source pages.

## What it includes

- FastAPI backend with `POST /api/ask`
- FAISS similarity search with sentence-transformer embeddings
- Groq-powered answer synthesis
- Single-page frontend in `web/index.html`
- Source file, page, distance, and snippet display

## Run locally

```powershell
git clone https://github.com/esha389/ASK_DOCS_RAG.git
cd ASK_DOCS_RAG
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Add your `GROQ_API_KEY` to `.env`, then start the app:

```powershell
uvicorn api:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

Place PDFs, text files, CSVs, Word files, or JSON files under `data/`. The FAISS index is generated locally on first startup when needed.

## API

```http
POST /api/ask
Content-Type: application/json

{"query": "What is attention?", "top_k": 3}
```

The response contains an `answer` and a `sources` array.
