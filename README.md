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
 
**A context-aware AI assistant built to represent Mohamed Aymen.**  
Ask it anything about my skills, projects, or experience — it knows everything.
 
[🌐 Live Portfolio](https://poortflio.netlify.app/) • [📖 API Docs](https://mohamed10ayman24-personal-ai-agent.hf.space/docs) • [🚀 Live API](https://mohamed10ayman24-personal-ai-agent.hf.space)
 
</div>
---
 
## 📌 Overview
 
This project is a **production-ready RAG (Retrieval-Augmented Generation) pipeline** that acts as a personal AI representative. Instead of a static bio, visitors on my portfolio can have a real conversation with an AI that knows my actual CV, GitHub projects, and LinkedIn experience — all grounded in real data, no hallucinations.
 
---
 
## 🚀 Key Features
 
- **🔍 Dynamic RAG Pipeline** — Ingests data from PDFs (CV), ZIP files (LinkedIn exports), and the GitHub API to build a local FAISS vector store
- **🧠 Powered by Gemini** — Uses Google's Gemini for both LLM responses and text embeddings (`gemini-embedding-001`)
- **⚡ FastAPI Backend** — High-performance async API with CORS support for seamless frontend integration
- **🐳 Dockerized Deployment** — Fully containerized for consistent behavior across all environments
- **☁️ Hosted on Hugging Face Spaces** — Live and publicly accessible with zero cold-start issues
- **📦 Git LFS Integration** — Professional handling of large binary assets (PDFs, ZIPs) via Git Large File Storage
---
 
## 🛠️ Tech Stack
 
| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.9 |
| **API Framework** | FastAPI + Uvicorn |
| **AI Orchestration** | LangChain 0.3 |
| **Vector Database** | FAISS (CPU) |
| **LLM & Embeddings** | Google GenAI — Gemini |
| **Data Sources** | PDF (CV), GitHub API, LinkedIn CSV Export |
| **Infrastructure** | Docker, Hugging Face Spaces, Git LFS |
 
---
 
## 🏗️ Architecture
 
```
┌─────────────────────────────────────────────────────┐
│                   Data Sources                       │
│  📄 CV (PDF)  │  🐙 GitHub API  │  💼 LinkedIn ZIP  │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              LangChain Ingestion Pipeline            │
│   Text Splitting → Gemini Embeddings → FAISS Store  │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                  FastAPI Backend                     │
│   POST /ask  │  GET /health  │  GET /docs (Swagger) │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│              Portfolio Frontend                      │
│         https://poortflio.netlify.app/               │
│   Hero Section Chat Widget — powered by this API    │
└─────────────────────────────────────────────────────┘
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
  "sources_loaded": 5
}
```
 
### `GET /health`
Health check endpoint.
 
```json
{ "status": "ok", "ready": true }
```
 
### `POST /ask`
Ask the agent a question about Mohamed.
 
**Request:**
```json
{
  "question": "What are your main technical skills?",
  "session_id": "optional-session-id"
}
```
 
**Response:**
```json
{
  "answer": "Mohamed's main skills include Python (Async, OOP), TensorFlow, FastAPI, OpenCV, DeepFace, Gemini API, and the Microsoft Power Platform stack...",
  "sources": ["CV", "GitHub", "LinkedIn"],
  "name": "Mohamed Aymen Salem"
}
```
 
### Try it live:
🔗 **Swagger UI:** [`/docs`](https://mohamed10ayman24-personal-ai-agent.hf.space/docs)
 
---
 
## 🗂️ Project Structure
 
```
personal-ai-agent/
├── main.py                  # CLI entry point
├── api.py                   # FastAPI app
├── Dockerfile               # Container config
├── requirements.txt
├── .env.example
├── src/
│   ├── cv_loader.py         # PDF ingestion
│   ├── github_fetcher.py    # GitHub API scraper
│   ├── linkedin_loader.py   # LinkedIn CSV parser
│   └── rag_chain.py         # Gemini embeddings + LangChain RAG
└── data/
    ├── cv.pdf
    ├── linkedin_export.zip
    └── vectorstore/         # FAISS index (auto-generated)
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
# Fill in your keys:
# GOOGLE_API_KEY=AIza...
# GITHUB_TOKEN=ghp_...
# GITHUB_USERNAME=MohammedAymen
# YOUR_NAME=Mohamed Aymen Salem
```
 
### 3. Add your data
 
```
data/cv.pdf               ← your CV
data/linkedin_export.zip  ← LinkedIn data export
```
 
### 4. Run
 
```bash
# CLI mode
python main.py
 
# API mode
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```
 
---
 
## 🐳 Docker
 
```bash
docker build -t personal-ai-agent .
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=your_key \
  -e GITHUB_USERNAME=MohammedAymen \
  -e YOUR_NAME="Mohamed Aymen Salem" \
  personal-ai-agent
```
 
---
 
## ☁️ Deployment on Hugging Face Spaces
 
This project is hosted on Hugging Face Spaces as a Docker space.
 
### Steps taken:
 
1. **Git LFS Setup** — Initialized LFS to track binary files:
   ```bash
   git lfs install
   git lfs track "*.pdf" "*.zip"
   ```
 
2. **History Migration** — Cleaned existing binaries from Git history:
   ```bash
   git lfs migrate import --include="*.pdf,*.zip" --everything
   ```
 
3. **Secrets Management** — `GOOGLE_API_KEY` and other secrets are stored in Hugging Face Space Secrets (not in the repo).
4. **Push & deploy:**
   ```bash
   git remote add space https://huggingface.co/spaces/mohamed10ayman24/personal-ai-agent
   git push space main
   ```
 
---
 
## 💡 Example Questions
 
```
"What are Mohamed's main technical skills?"
"Tell me about the Blockchain Voting project"
"Does he have experience with FastAPI?"
"What is his educational background?"
"ما هي مشاريعه البرمجية؟"
"هل لديه خبرة في الذكاء الاصطناعي؟"
```
 
---
 
## 🌐 Live Integration
 
This API powers the **AI Chat Widget** on my personal portfolio website.  
Visitors can ask questions about me directly from the hero section of:
 
> 🔗 **[https://poortflio.netlify.app/](https://poortflio.netlify.app/)**
 
The widget connects to the Hugging Face Spaces endpoint in real-time, with an offline fallback for when the API is warming up.
 
---
 
## 👨‍💻 Author
 
**Mohamed Aymen Salem**  
AI Programmer & Developer — Specialist in Machine Learning, Computer Vision & NLP  
📍 Port Said, Egypt
 
[![GitHub](https://img.shields.io/badge/GitHub-MohammedAymen-181717?style=flat&logo=github)](https://github.com/MohammedAymen)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Mohamed%20Aymen-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/in/mohamed-aymen-750236225)
[![Portfolio](https://img.shields.io/badge/Portfolio-Live-00C7B7?style=flat&logo=netlify)](https://poortflio.netlify.app/)
 














