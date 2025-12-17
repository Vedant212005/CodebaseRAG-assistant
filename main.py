# main.py
import os
import time
import uuid
import shutil
import threading
import json
import faiss
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv

from utils.repo_utils import clone_github_repo
from ingest import run_ingest
from build_vector_index import build_vector_index

# =====================
# CONFIG
# =====================
load_dotenv()

import tempfile
import os

BASE_SESSION_DIR = os.path.join(tempfile.gettempdir(), "code_sessions")

SESSION_TTL_SECONDS = 30 * 60  # 30 minutes
TOP_K = 5
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

os.makedirs(BASE_SESSION_DIR, exist_ok=True)

# =====================
# GEMINI
# =====================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY missing")

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

# =====================
# APP INIT
# =====================
app = FastAPI(title="RAG CodeBase API")

embed_model = SentenceTransformer(MODEL_NAME)

# =====================
# SESSION CACHE
# =====================
SESSION_CACHE = {}
CACHE_LOCK = threading.Lock()

# =====================
# REQUEST MODELS
# =====================
class RepoRequest(BaseModel):
    repo_url: str

class QueryRequest(BaseModel):
    query: str

# =====================
# SESSION HELPERS
# =====================
def get_or_create_session_id(request: Request, response: Response) -> str:
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            samesite="lax"
        )
    return session_id


def session_dir(session_id: str) -> str:
    return os.path.join(BASE_SESSION_DIR, f"session_{session_id}")


def load_session_into_memory(session_id: str, sdir: str):
    index = faiss.read_index(os.path.join(sdir, "code_index.faiss"))
    metadata = json.load(open(os.path.join(sdir, "metadata.json")))
    chunks = json.load(open(os.path.join(sdir, "code_chunks.json")))

    SESSION_CACHE[session_id] = {
        "index": index,
        "metadata": metadata,
        "chunks": chunks,
        "last_access": time.time()
    }


# =====================
# CLEANUP THREAD
# =====================
def cleanup_sessions():
    while True:
        time.sleep(300)  # every 5 min
        now = time.time()

        with CACHE_LOCK:
            expired = [
                sid for sid, data in SESSION_CACHE.items()
                if now - data["last_access"] > SESSION_TTL_SECONDS
            ]

            for sid in expired:
                SESSION_CACHE.pop(sid, None)
                shutil.rmtree(session_dir(sid), ignore_errors=True)

threading.Thread(target=cleanup_sessions, daemon=True).start()

# =====================
# ROUTES
# =====================
@app.post("/process_repo")
def process_repo(request: Request, response: Response, body: RepoRequest):
    session_id = get_or_create_session_id(request, response)
    sdir = session_dir(session_id)

    try:
        shutil.rmtree(sdir, ignore_errors=True)
        os.makedirs(sdir, exist_ok=True)

        repo_path = clone_github_repo(body.repo_url, base_dir=sdir)
        run_ingest(repo_path, out_file=os.path.join(sdir, "code_chunks.json"))
        build_vector_index(sdir)

        load_session_into_memory(session_id, sdir)

        return {"message": "Repository processed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
def query_repo(request: Request, response: Response, body: QueryRequest):
    session_id = get_or_create_session_id(request, response)

    with CACHE_LOCK:
        if session_id not in SESSION_CACHE:
            sdir = session_dir(session_id)
            if not os.path.exists(sdir):
                raise HTTPException(400, "No repository processed yet.")
            load_session_into_memory(session_id, sdir)

        SESSION_CACHE[session_id]["last_access"] = time.time()
        data = SESSION_CACHE[session_id]

    query_emb = embed_model.encode(
        [body.query],
        normalize_embeddings=True
    ).astype("float32")

    D, I = data["index"].search(query_emb, TOP_K)

    context = []
    for idx in I[0]:
        m = data["metadata"][idx]
        for c in data["chunks"]:
            if c["file"] == m["file"] and c["name"] == m["name"]:
                context.append(c["code"])
                break

    if not context:
        return {"response": "No relevant code found."}

    prompt = f"""
Use ONLY the code context below to answer.

{chr(10).join(context)}

Question:
{body.query}
"""

    answer = gemini_model.generate_content(prompt).text
    return {"response": answer}
