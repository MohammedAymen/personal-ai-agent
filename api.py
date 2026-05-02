import os
import sys
import time
import shutil
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from src.cv_loader import load_cv
from src.github_fetcher import load_github
from src.linkedin_loader import load_linkedin
from src.rag_chain import build_vectorstore, build_qa_chain


RATE_LIMIT          = int(os.getenv("RATE_LIMIT", 5))       
RATE_LIMIT_WINDOW   = int(os.getenv("RATE_LIMIT_WINDOW", 60)) 
ADMIN_SECRET        = os.getenv("ADMIN_SECRET", "change-me-please")
ALLOWED_ORIGINS     = os.getenv("ALLOWED_ORIGINS", "*").split(",")


app = FastAPI(
    title="Personal AI Agent API",
    description="RAG-powered API that answers questions about Mohamed Ayman Salem",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


vectorstore  = None
documents    = []
your_name    = os.getenv("YOUR_NAME", "Mohamed Ayman Salem")
startup_time = time.time()


_session_chains: dict = {}
SESSION_TTL     = int(os.getenv("SESSION_TTL", 1800))  
_session_times: dict = {}


_rate_store: dict = defaultdict(list)



class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"

class AnswerResponse(BaseModel):
    answer: str
    sources: list
    name: str

class StatusResponse(BaseModel):
    status: str
    name: str
    sources_loaded: int
    uptime_seconds: float
    ready: bool

class RebuildResponse(BaseModel):
    success: bool
    message: str
    sources_loaded: int



def rate_limit(request: Request):
    ip  = request.client.host
    now = time.time()

   
    _rate_store[ip] = [t for t in _rate_store[ip] if now - t < RATE_LIMIT_WINDOW]

    if len(_rate_store[ip]) >= RATE_LIMIT:
        retry_after = int(RATE_LIMIT_WINDOW - (now - _rate_store[ip][0]))
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {retry_after}s "
                   f"(max {RATE_LIMIT} requests per {RATE_LIMIT_WINDOW}s).",
            headers={"Retry-After": str(retry_after)},
        )

    _rate_store[ip].append(now)



def verify_admin(request: Request):
    token = request.headers.get("X-Admin-Secret", "")
    if token != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid or missing admin secret.")



def _cleanup_expired_sessions():
    """شيل الـ sessions اللي انتهت"""
    now = time.time()
    expired = [sid for sid, t in _session_times.items() if now - t > SESSION_TTL]
    for sid in expired:
        _session_chains.pop(sid, None)
        _session_times.pop(sid, None)


def get_session_chain(session_id: str):
    """جيب الـ chain بتاع الـ session دي، أو اعمل واحد جديد"""
    _cleanup_expired_sessions()

    if session_id not in _session_chains:
        _session_chains[session_id] = build_qa_chain(vectorstore, your_name)

    _session_times[session_id] = time.time()
    return _session_chains[session_id]
def _load_documents() -> list:
    docs = []

    cv_path = os.getenv("CV_PDF_PATH", "data/cv.pdf")
    try:
        docs.extend(load_cv(cv_path))
    except FileNotFoundError:
        print(f"Warning: CV not found at {cv_path}")

    github_user  = os.getenv("GITHUB_USERNAME", "")
    github_token = os.getenv("GITHUB_TOKEN", "")
    if github_user:
        docs.extend(load_github(github_user, github_token))

    linkedin_path = os.getenv("LINKEDIN_CSV_PATH", "data/linkedin_export.zip")
    docs.extend(load_linkedin(linkedin_path))

    return docs



@app.on_event("startup")
async def startup_event():
    global vectorstore, documents
    print("Loading data sources...")
    documents   = _load_documents()
    print(f"Loaded {len(documents)} sources. Building vector store...")
    vectorstore = build_vectorstore(documents)
    print("API ready!")



@app.get("/", response_model=StatusResponse)
async def root():
    return StatusResponse(
        status="running",
        name=your_name,
        sources_loaded=len(documents),
        uptime_seconds=round(time.time() - startup_time, 1),
        ready=vectorstore is not None,
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "ready": vectorstore is not None,
        "uptime_seconds": round(time.time() - startup_time, 1),
        "active_sessions": len(_session_chains),
        "rate_limit": f"{RATE_LIMIT} req/{RATE_LIMIT_WINDOW}s",
    }


@app.post("/ask", response_model=AnswerResponse, dependencies=[Depends(rate_limit)])
async def ask(request: QuestionRequest):
    if vectorstore is None:
        raise HTTPException(status_code=503, detail="AI not ready yet, please wait...")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if len(request.question) > 500:
        raise HTTPException(status_code=400, detail="Question too long (max 500 chars).")

    try:
       
        chain  = get_session_chain(request.session_id or "default")
        result = chain.invoke({"question": request.question})

        answer      = result.get("answer", "")
        source_docs = result.get("source_documents", [])
        sources     = list({doc.metadata.get("source", "Unknown") for doc in source_docs})

        return AnswerResponse(answer=answer, sources=sources, name=your_name)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/admin/rebuild", response_model=RebuildResponse,
          dependencies=[Depends(verify_admin)])
async def admin_rebuild():
   
    global vectorstore, documents, _session_chains, _session_times
    try:
        documents   = _load_documents()
        vectorstore = build_vectorstore(documents, force_rebuild=True)
      
        _session_chains.clear()
        _session_times.clear()
        return RebuildResponse(
            success=True,
            message="Vector store rebuilt and all sessions reset.",
            sources_loaded=len(documents),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rebuild failed: {e}")


@app.post("/admin/upload-cv", dependencies=[Depends(verify_admin)])
async def admin_upload_cv(request: Request):
    """
    Upload a new CV PDF to replace the existing one.
    Send as raw bytes with Content-Type: application/pdf
    """
    cv_path = Path(os.getenv("CV_PDF_PATH", "data/cv.pdf"))
    cv_path.parent.mkdir(parents=True, exist_ok=True)

    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="No file content received.")

    # backup old CV
    if cv_path.exists():
        shutil.copy(cv_path, cv_path.with_suffix(".pdf.bak"))

    cv_path.write_bytes(body)
    return {
        "success": True,
        "message": f"CV uploaded ({len(body):,} bytes). Call /admin/rebuild to re-index.",
        "path": str(cv_path),
    }


@app.get("/admin/status", dependencies=[Depends(verify_admin)])
async def admin_status():
    """Detailed system status for admin monitoring."""
    return {
        "ready": vectorstore is not None,
        "sources_loaded": len(documents),
        "uptime_seconds": round(time.time() - startup_time, 1),
        "active_sessions": len(_session_chains),
        "session_ttl_seconds": SESSION_TTL,
        "rate_limit_config": {
            "max_requests": RATE_LIMIT,
            "window_seconds": RATE_LIMIT_WINDOW,
        },
        "active_ips": len(_rate_store),
        "vectorstore_exists": Path("data/vectorstore").exists(),
        "cv_exists": Path(os.getenv("CV_PDF_PATH", "data/cv.pdf")).exists(),
        "linkedin_exists": Path(os.getenv("LINKEDIN_CSV_PATH", "data/linkedin_export.zip")).exists(),
    }


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)