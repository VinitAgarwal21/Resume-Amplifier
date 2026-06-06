# 🚀 Resume Amplifier

> **AI-powered resume analysis, optimization, and career toolkit — built with LangGraph + Gemini**

[![Live Demo](https://img.shields.io/badge/🤗%20Live%20Demo-Hugging%20Face%20Spaces-yellow)](https://huggingface.co/spaces/Vinit-Agarwal/Resume-Amplifier)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green)](https://github.com/langchain-ai/langgraph)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red?logo=streamlit)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal?logo=fastapi)](https://fastapi.tiangolo.com)

---

## 🌐 Live Demo

👉 **[Try it on Hugging Face Spaces](https://huggingface.co/spaces/Vinit-Agarwal/Resume-Amplifier)**

---

## 📸 Screenshots

![Fit Score](screenshots/image.png)
![Strengths & Weaknesses](screenshots/image-1.png)
![Q&A](screenshots/image-2.png)
![Improved Resume](screenshots/image-3.png)
![Interview Prep](screenshots/image-4.png)

---

## ✨ Features

| Tab | What it does |
|-----|-------------|
| 📊 **Fit Score** | ATS-style match score (0–100) with keyword and 4-category breakdown |
| 💪 **Strengths & Weaknesses** | Detailed pros/cons + critical gaps + quick wins vs the JD |
| 💬 **Q&A** | Chat-style interface — ask anything about the JD or resume |
| ✨ **Improved Resume** | AI-rewrites your resume tailored to the JD (no fabrication) |
| 🎤 **Interview Prep** | 10–12 categorized questions with tailored suggested answers |
| ✉️ **Cover Letter** | Tailored cover letter matching the JD tone and requirements |
| 📥 **Export** | Download everything as **PDF**, **DOCX**, or **TXT** |

---

## 🏗️ Architecture

```
Streamlit UI / FastAPI
        │
        ▼
LangGraph StateGraph
        │
        ├── fit_score_node              → ATS score + keyword analysis (JSON)
        ├── strengths_weaknesses_node   → structured pros/cons (JSON)
        ├── qa_node                     → contextual Q&A (text)
        ├── resume_rewriter_node        → tailored resume (text)
        ├── interview_prep_node         → questions + answers (JSON)
        └── cover_letter_node           → cover letter (text)
```

Each feature invokes the LangGraph state machine with a different `task` value. A router conditionally dispatches to the correct node, which calls Gemini 2.5 Flash and returns structured output.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Orchestration** | [LangGraph](https://github.com/langchain-ai/langgraph) — state graph with conditional routing |
| **LLM** | [Gemini 2.5 Flash](https://aistudio.google.com) via `langchain-google-genai` |
| **Frontend** | [Streamlit](https://streamlit.io) — dark-themed, tabbed UI |
| **Backend API** | [FastAPI](https://fastapi.tiangolo.com) + [Uvicorn](https://www.uvicorn.org) |
| **PDF Export** | [ReportLab](https://www.reportlab.com) |
| **DOCX Export** | [python-docx](https://python-docx.readthedocs.io) |
| **PDF Parsing** | [PyPDF2](https://pypdf2.readthedocs.io) |
| **Containerization** | Docker + Docker Compose |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev) |

---

## 📁 Project Structure

```
resume-amplifier/
├── app.py               # Streamlit frontend
├── agent.py             # LangGraph agent — all AI logic
├── main.py              # FastAPI backend
├── api_models.py        # Pydantic request/response schemas
├── export_utils.py      # PDF & DOCX export functions
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── screenshots/
```

---

## 🚀 Setup & Run

### Prerequisites
- Python 3.12+
- A free [Google API key](https://aistudio.google.com/apikey)

### Option 1 — Local

```bash
# 1. Clone the repo
git clone https://github.com/VinitAgarwal21/Resume-Amplifier
cd resume-amplifier

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run Streamlit UI
streamlit run app.py
# → http://localhost:8501

# Or run the FastAPI backend
uvicorn main:app --reload --port 8000
# → http://localhost:8000/docs
```

### Option 2 — Docker

```bash
# 1. Copy env file and add your API key
cp .env.example .env

# 2. Run API only
docker-compose up --build

# 3. Run API + Streamlit UI
docker-compose --profile ui up --build

# API  → http://localhost:8000
# Docs → http://localhost:8000/docs
# UI   → http://localhost:8501
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Health check |
| POST | `/score` | ATS fit score + keyword analysis |
| POST | `/strengths` | Strengths, weaknesses, gaps, quick wins |
| POST | `/qa` | Q&A about JD or resume |
| POST | `/rewrite` | ATS-optimized resume rewrite |
| POST | `/interview` | Interview questions + suggested answers |
| POST | `/cover-letter` | Tailored cover letter |
| POST | `/export/resume` | Download resume as PDF or DOCX |
| POST | `/export/cover-letter` | Download cover letter as PDF or DOCX |
| POST | `/export/interview` | Download interview guide as DOCX or TXT |

Pass your Google API key via the `X-Google-Api-Key` request header.

**Example:**
```bash
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -H "X-Google-Api-Key: AIza..." \
  -d '{
    "jd_text": "We are looking for a Python developer...",
    "resume_text": "John Doe, Python Developer with 4 years..."
  }'
```

Interactive docs at `http://localhost:8000/docs`.

---

## 📄 Supported File Formats

- Plain text (`.txt`)
- PDF (`.pdf`) — text-based; scanned PDFs may not extract well
- Word documents (`.docx`)

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Optional | Can also be entered in the UI sidebar per session |

```bash
# Set before running to skip the UI key input
export GOOGLE_API_KEY=AIza...
streamlit run app.py
```

---