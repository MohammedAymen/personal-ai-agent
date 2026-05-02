---
title: Personal AI Agent
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---
# 🤖 Personal AI Agent — RAG-Powered Portfolio Assistant

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.3+-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Spaces-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)

### *"Don't just read my CV — talk to it."*

**A production-ready AI assistant that represents me 24/7.**  
Powered by real data from my CV, GitHub & LinkedIn. No hallucinations. No static bios.  
Just accurate, context-aware answers — in any language.

[🌐 Live Portfolio](https://poortflio.netlify.app/) • [📖 API Docs](https://mohamed10ayman24-personal-ai-agent.hf.space/docs) • [🚀 Live API](https://mohamed10ayman24-personal-ai-agent.hf.space)

</div>

---

## 📋 Table of Contents

- [📌 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [🏗️ Architecture](#️-architecture)
- [📡 API Reference](#-api-reference)
- [🔐 Admin Endpoints](#-admin-endpoints)
- [🗂️ Project Structure](#️-project-structure)
- [⚙️ Local Setup](#️-local-setup)
- [🐳 Docker](#-docker)
- [☁️ Deployment on Hugging Face Spaces](#️-deployment-on-hugging-face-spaces)
- [💡 Example Questions](#-example-questions)
- [🌐 Live Integration](#-live-integration)
- [👨‍💻 Author](#-author)

---

## 📌 Overview

Most portfolios are static pages. Mine talks back.

This project is a **production-grade RAG (Retrieval-Augmented Generation) pipeline** that acts as a live AI representative of my professional identity. Instead of making recruiters or collaborators dig through a PDF, they can just ask — and get precise, grounded answers pulled directly from my actual data.

Built from scratch using LangChain, Google Gemini, and FastAPI, deployed on Hugging Face Spaces, and embedded live into my portfolio. Every feature was engineered with real-world reliability in mind: per-session memory, rate limiting, admin controls, and a smart fallback system so the chat never goes dark.

> **The goal:** Replace "Here's my CV" with "Ask me anything."

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **Dynamic RAG Pipeline** | Ingests CV (PDF), LinkedIn export (ZIP), and GitHub API — builds a FAISS vector index automatically |
| 🧠 **Gemini-Powered** | Uses `gemini-embedding-001` for embeddings and `gemini-2.0-flash` for blazing-fast responses |
| 💬 **Multi-turn Conversations** | Per-session memory — each visitor gets their own isolated conversation history (auto-expires after 30 min) |
| ⏱️ **Rate Limiting** | IP-based protection against abuse — 5 req/min by default, fully configurable via `.env` |
| 🔐 **Admin Controls** | Secure endpoints to upload a new CV, rebuild the index, and monitor system health — all without redeployment |
| 💚 **Health Monitoring** | Live status on uptime, active sessions, vectorstore state, and connected data sources |
| 🔗 **Configurable CORS** | Allowlist specific domains via `ALLOWED_ORIGINS` — production-ready for any frontend |
| 🛡️ **Smart Fallback** | If the API is cold-starting, the frontend answers from a curated local dataset — zero downtime for visitors |
| 🐳 **Dockerized** | Single `docker run` command — consistent behavior from local dev to cloud deployment |
| ☁️ **Hugging Face Spaces** | Live, public, and free — with Git LFS for clean binary asset management |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.9+ |
| **API Framework** | FastAPI + Uvicorn |
| **AI Orchestration** | LangChain 0.3 |
| **LLM** | Google Gemini 2.0 Flash |
| **Embeddings** | Google Gemini Embedding 001 |
| **Vector Database** | FAISS (CPU) |
| **Session Memory** | LangChain ConversationBufferWindowMemory |
| **Data Sources** | PDF (CV), GitHub REST API, LinkedIn CSV Export |
| **Infrastructure** | Docker, Hugging Face Spaces, Git LFS |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                      Data Sources                         │
│   📄 CV (PDF)   │   🐙 GitHub API   │   💼 LinkedIn ZIP  │
└─────────────────────────┬────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│               LangChain Ingestion Pipeline                │
│    Text Splitting → Gemini Embeddings → FAISS Store       │
└─────────────────────────┬────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│                   FastAPI Backend                         │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  POST /ask  │  │  GET /health │  │  /admin/*      │  │
│  │ + Rate Limit│  │  + Uptime    │  │  + Auth Guard  │  │
│  │ + Session   │  │  + Sessions  │  │  + CV Upload   │  │
│  │   Memory    │  │              │  │  + Rebuild     │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
└─────────────────────────┬────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│                  Portfolio Frontend                        │
│            https://poortflio.netlify.app/                 │
│   Hero Section Chat Widget — live, session-aware          │
│   Smart fallback when API is warming up                   │
└──────────────────────────────────────────────────────────┘
```

---

## 📡 API Reference

**Base URL:** `https://mohamed10ayman24-personal-ai-agent.hf.space`

### `GET /`
Returns agent status and basic info.

```json
{
  "status": "running",
  "name": "Mohamed Aymen Salem",
  "sources_loaded": 5,
  "uptime_seconds": 3600.0,
  "ready": true
}
```

### `GET /health`
Health check with session and rate limit info.

```json
{
  "status": "ok",
  "ready": true,
  "uptime_seconds": 3600.0,
  "active_sessions": 3,
  "rate_limit": "5 req/60s"
}
```

### `POST /ask`
Ask the agent anything about Mohamed. Supports multi-turn conversations via `session_id`.

**Request:**
```json
{
  "question": "What are your main technical skills?",
  "session_id": "user_abc123"
}
```

**Response:**
```json
{
  "answer": "Mohamed's core skills include Python (Async, OOP), TensorFlow, FastAPI, OpenCV, DeepFace, Gemini API, and the full Microsoft Power Platform stack...",
  "sources": ["CV", "GitHub", "LinkedIn"],
  "name": "Mohamed Aymen Salem"
}
```

**Rate limit error (429):**
```json
{
  "detail": "Rate limit exceeded. Try again in 45s (max 5 requests per 60s)."
}
```

🔗 **Try it live — Swagger UI:** [`/docs`](https://mohamed10ayman24-personal-ai-agent.hf.space/docs)

---

## 🔐 Admin Endpoints

All admin endpoints require the following header:
```
X-Admin-Secret: your-secret-here
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/rebuild` | `POST` | Rebuild FAISS index from all sources + reset all sessions |
| `/admin/upload-cv` | `POST` | Upload a new CV PDF (raw bytes) — auto-backed up |
| `/admin/status` | `GET` | Full system status: sessions, files, rate limits, uptime |

**Rebuild after updating your CV:**
```bash
curl -X POST https://mohamed10ayman24-personal-ai-agent.hf.space/admin/rebuild \
  -H "X-Admin-Secret: your-secret-here"
```

**Upload a new CV:**
```bash
curl -X POST https://mohamed10ayman24-personal-ai-agent.hf.space/admin/upload-cv \
  -H "X-Admin-Secret: your-secret-here" \
  -H "Content-Type: application/pdf" \
  --data-binary @new_cv.pdf
```

**Check system status:**
```bash
curl https://mohamed10ayman24-personal-ai-agent.hf.space/admin/status \
  -H "X-Admin-Secret: your-secret-here"
```

---

## 🗂️ Project Structure

```
personal-ai-agent/
├── main.py                  # CLI entry point (interactive chat)
├── api.py                   # FastAPI app — all endpoints + session management
├── Dockerfile               # Container config
├── requirements.txt
├── .env.example             # All configurable variables
├── src/
│   ├── cv_loader.py         # PDF ingestion via pypdf
│   ├── github_fetcher.py    # GitHub REST API scraper
│   ├── linkedin_loader.py   # LinkedIn ZIP/CSV parser
│   └── rag_chain.py         # Gemini embeddings + LangChain RAG chain
└── data/
    ├── cv.pdf               # Your CV (tracked via Git LFS)
    ├── linkedin_export.zip  # LinkedIn data export (tracked via Git LFS)
    └── vectorstore/         # FAISS index (auto-generated, gitignored)
```

---

## ⚙️ Local Setup

### 1. Clone & install

```bash
git clone https://github.com/MohammedAymen/personal-ai-agent
cd personal-ai-agent
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Fill in `.env`:

```env
# Required
GOOGLE_API_KEY=AIza...
YOUR_NAME=Mohamed Aymen Salem

# GitHub (optional but recommended)
GITHUB_TOKEN=ghp_...
GITHUB_USERNAME=MohammedAymen

# File paths
CV_PDF_PATH=data/cv.pdf
LINKEDIN_CSV_PATH=data/linkedin_export.zip

# Security
ADMIN_SECRET=your-strong-secret-here

# CORS — comma-separated list of allowed origins
ALLOWED_ORIGINS=https://poortflio.netlify.app,http://localhost:3000

# Rate limiting
RATE_LIMIT=5           # max requests per window per IP
RATE_LIMIT_WINDOW=60   # window in seconds

# Session memory
SESSION_TTL=1800       # seconds before inactive session expires (default: 30 min)
```

### 3. Add your data

```
data/cv.pdf               ← your CV (PDF)
data/linkedin_export.zip  ← LinkedIn data export
```

### 4. Run

```bash
# Interactive CLI mode
python main.py

# API server mode
uvicorn api:app --reload --host 0.0.0.0 --port 8000
# Then open: http://localhost:8000/docs
```

---

## 🐳 Docker

```bash
docker build -t personal-ai-agent .

docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=your_key \
  -e GITHUB_TOKEN=your_github_token \
  -e GITHUB_USERNAME=MohammedAymen \
  -e YOUR_NAME="Mohamed Aymen Salem" \
  -e ADMIN_SECRET=your-secret \
  personal-ai-agent
```

**`Dockerfile` overview:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## ☁️ Deployment on Hugging Face Spaces

This project runs as a **Docker Space** on Hugging Face — free, public, and always on.

### Steps:

**1. Git LFS — track binary files:**
```bash
git lfs install
git lfs track "*.pdf" "*.zip"
git add .gitattributes
```

**2. Clean history (if binaries were committed before LFS):**
```bash
git lfs migrate import --include="*.pdf,*.zip" --everything
```

**3. Set secrets in Hugging Face (never commit these):**
```
GOOGLE_API_KEY     → your Gemini API key
ADMIN_SECRET       → your admin password
GITHUB_TOKEN       → your GitHub token
```

**4. Push & deploy:**
```bash
git remote add space https://huggingface.co/spaces/mohamed10ayman24/personal-ai-agent
git push space main
```

The Space rebuilds automatically on every push. ✅

---

## 💡 Example Questions

```
"What are Mohamed's main technical skills?"
"Tell me about the Blockchain Voting System project"
"Does he have experience with FastAPI or async Python?"
"What is his educational background?"
"Has he worked with computer vision before?"
"What certifications does he have?"
"ما هي مشاريعه في مجال الذكاء الاصطناعي؟"
"هل لديه خبرة في Power Platform؟"
```

---

## 🌐 Live Integration

This API is the brain behind the **AI Chat Widget** embedded in the hero section of my portfolio. Every visitor gets their own isolated conversation — powered by real data, not a script.

> 🔗 **[https://poortflio.netlify.app/](https://poortflio.netlify.app/)**

**How it works for visitors:**
1. Page loads → a unique `session_id` is generated in the browser
2. Visitor types a question → sent to the Hugging Face API with their session ID
3. The API retrieves relevant context from the vector store and responds with Gemini
4. Conversation history is maintained per session for natural follow-up questions
5. If the API is cold-starting → smart fallback answers from local curated data

---

## 👨‍💻 Author

**Mohamed Aymen Salem**  
AI Engineer & Developer — Machine Learning · Computer Vision · NLP  
📍 Port Said, Egypt

[![GitHub](https://img.shields.io/badge/GitHub-MohammedAymen-181717?style=flat&logo=github)](https://github.com/MohammedAymen)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Mohamed%20Aymen-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/in/mohamed-aymen-750236225)
[![Portfolio](https://img.shields.io/badge/Portfolio-Live-00C7B7?style=flat&logo=netlify)](https://poortflio.netlify.app/)

---

*Built with ❤️ · Powered by Gemini · Deployed on Hugging Face*