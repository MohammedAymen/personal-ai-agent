# -*- coding: utf-8 -*-
"""
api.py - FastAPI wrapper for the Personal AI Agent
شغّله بـ: uvicorn api:app --reload
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

# ---- Load data & build chain once at startup ----
from src.cv_loader import load_cv
from src.github_fetcher import load_github
from src.linkedin_loader import load_linkedin
from src.rag_chain import build_vectorstore, build_qa_chain

app = FastAPI(
    title="Personal AI Agent API",
    description="API that answers questions about Mohamed Ayman Salem",
    version="1.0.0",
)

# Allow all origins so your portfolio website can call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Global state ----
qa_chain = None
your_name = os.getenv("YOUR_NAME", "Mohamed Ayman Salem")


# ---- Pydantic models ----
class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"


class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]
    name: str


class StatusResponse(BaseModel):
    status: str
    name: str
    sources_loaded: int


# ---- Startup: load everything ----
@app.on_event("startup")
async def startup_event():
    global qa_chain

    print("Loading data sources...")
    documents = []

    cv_path = os.getenv("CV_PDF_PATH", "data/cv.pdf")
    try:
        documents.extend(load_cv(cv_path))
    except FileNotFoundError:
        print(f"Warning: CV not found at {cv_path}")

    github_user = os.getenv("GITHUB_USERNAME", "")
    github_token = os.getenv("GITHUB_TOKEN", "")
    if github_user:
        documents.extend(load_github(github_user, github_token))

    linkedin_path = os.getenv("LINKEDIN_CSV_PATH", "data/linkedin_export.zip")
    documents.extend(load_linkedin(linkedin_path))

    print(f"Loaded {len(documents)} sources. Building vector store...")
    vectorstore = build_vectorstore(documents)
    qa_chain = build_qa_chain(vectorstore, your_name)
    print("API ready!")


# ---- Endpoints ----
@app.get("/", response_model=StatusResponse)
async def root():
    return StatusResponse(
        status="running",
        name=your_name,
        sources_loaded=5,
    )


@app.get("/health")
async def health():
    return {"status": "ok", "ready": qa_chain is not None}


@app.post("/ask", response_model=AnswerResponse)
async def ask(request: QuestionRequest):
    if qa_chain is None:
        raise HTTPException(status_code=503, detail="AI not ready yet, please wait...")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = qa_chain.invoke({"question": request.question})
        answer = result.get("answer", "")
        source_docs = result.get("source_documents", [])
        sources = list({doc.metadata.get("source", "Unknown") for doc in source_docs})

        return AnswerResponse(
            answer=answer,
            sources=sources,
            name=your_name,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)