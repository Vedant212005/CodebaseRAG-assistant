# Codebase RAG Assistant

A full-stack Retrieval-Augmented Generation (RAG) project that accepts a GitHub repository URL, clones the repo, parses Python source code into structured JSON chunks using the AST, embeds those chunks with Sentence-Transformers, stores the vectors in FAISS, and answers user queries by retrieving relevant code and asking Google Gemini for a response.

---

## Key Features

- Clone a GitHub repository and extract all Python source files
- Parse functions, classes, methods and generate rich metadata using the Python AST
- Convert code snippets to vector embeddings using `sentence-transformers`
- Build an index with FAISS for fast semantic search
- Run semantic search on user queries and pass retrieved code context to **Gemini** for natural language answers
- Session-based caching to keep per-user repo index loaded temporarily

---

## Project Structure

- `backend/` - FastAPI backend that does cloning, ingestion, indexing, and query handling
  - `main.py` - FastAPI routes: `POST /process_repo` (ingest) and `POST /query` (semantic search + LLM)
  - `ingest.py` - AST-based parser that converts Python files into JSON chunks
  - `build_vector_index.py` - Creates embeddings (Sentence-Transformers) and stores FAISS index
  - `utils/repo_utils.py` - Helper for cloning repositories
  - `requirements.txt` - Python dependencies
  - `Dockerfile` - Docker image for backend

- `frontend/` - Vite + React frontend (UI components and repo input)

---

## Environment / Prerequisites

- Python 3.10+ (backend)
- Node.js 18+ (frontend)
- A valid Gemini API key (set `GEMINI_API_KEY` environment variable)

Backend dependencies are listed in `backend/requirements.txt` and include: `fastapi`, `uvicorn`, `sentence-transformers`, `faiss-cpu`, `google-generativeai`, `gitpython`, `python-dotenv`, etc.

---

## Quickstart

### 1) Backend (local)

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r backend/requirements.txt
```

2. Set environment variable for Gemini:

```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

# macOS / Linux
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

3. Start the backend (uvicorn):

```bash
# From repository root
cd backend
# set PORT if you want the Docker-compatible variable (defaults used in examples)
set PORT=10000
uvicorn main:app --host 0.0.0.0 --port ${PORT}
```

The backend exposes:
- POST `/process_repo` to ingest and build a per-session FAISS index
- POST `/query` to query against the loaded index

### 2) Frontend (local)

```bash
cd frontend
npm install
npm run dev
```

Open the UI (Vite defaults to `http://localhost:5173`) and paste a GitHub repo URL to start indexing.

### 3) Docker (backend)

Build and run the backend image:

```bash
cd backend
docker build -t codebase-rag-backend .
docker run -e GEMINI_API_KEY="<your-key>" -e PORT=10000 -p 10000:10000 codebase-rag-backend
```

---

## API Examples (curl)

1) Ingest / process a GitHub repo (stores session cookie in client):

```bash
curl -X POST "http://localhost:10000/process_repo" \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://github.com/<owner>/<repo>.git"}' \
  -c cookies.txt
```

2) Query (use same cookie file to preserve session):

```bash
curl -X POST "http://localhost:10000/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"How does the payment flow work?"}' \
  -b cookies.txt
```

---

## How it works (high-level)

1. The frontend sends a GitHub repo URL to `POST /process_repo`.
2. Backend clones the repo into a session directory (`utils/clone_github_repo`).
3. `ingest.py` walks Python files and uses `ast` to create JSON chunks with metadata and a `text_to_embed` field for each chunk.
4. `build_vector_index.py` computes embeddings with Sentence-Transformers, stores them as `.npy`, writes `metadata.json`, and saves a FAISS index file `code_index.faiss`.
5. On `POST /query`, the backend encodes the query with the same embedding model, runs a FAISS top-k search, extracts matching code chunks, and sends them as the prompt to Gemini for final text generation.
