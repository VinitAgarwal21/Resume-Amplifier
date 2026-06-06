"""
Resume Amplifier — FastAPI Backend
Run: uvicorn main:app --reload --host 0.0.0.0 --port 8000
Docs: http://localhost:8000/docs
"""

import os
import io
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from api_models import (
    ScoreRequest, ScoreResponse,
    StrengthsRequest, StrengthsResponse,
    QARequest, QAResponse,
    RewriteRequest, RewriteResponse,
    InterviewRequest, InterviewResponse,
    CoverLetterRequest, CoverLetterResponse,
    ExportResumeRequest, ExportCoverLetterRequest, ExportInterviewRequest,
    ErrorResponse,
)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm the LangGraph compiled graph on startup."""
    print("✅ Resume Amplifier API starting up…")
    yield
    print("👋 Resume Amplifier API shutting down…")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Resume Amplifier API",
    description=(
        "AI-powered resume analysis, scoring, rewriting, interview prep, "
        "and cover letter generation — built with LangGraph + Gemini."
    ),
    version="1.0.0",
    lifespan=lifespan,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── API key injection ─────────────────────────────────────────────────────────

def inject_api_key(x_google_api_key: str = Header(..., description="Your Google Gemini API key")):
    """
    Clients pass their Google API key via the X-Google-Api-Key header.
    It is set in the environment for this request only.
    """
    if not x_google_api_key.strip():
        raise HTTPException(status_code=401, detail="X-Google-Api-Key header is required.")
    os.environ["GOOGLE_API_KEY"] = x_google_api_key
    return x_google_api_key


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": "Resume Amplifier", "version": "1.0.0"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


# ── Analysis endpoints ────────────────────────────────────────────────────────

@app.post("/score", response_model=ScoreResponse, tags=["Analysis"],
          summary="ATS fit score",
          description="Returns a 0–100 match score, label, breakdown, and keyword analysis.")
def score(req: ScoreRequest, _: str = Depends(inject_api_key)):
    try:
        from agent import run_fit_score
        result = run_fit_score(req.jd_text, req.resume_text)
        # Ensure breakdown has all expected keys with defaults
        bd = result.get("breakdown", {})
        result["breakdown"] = {
            "skills_match":          bd.get("skills_match", 0),
            "experience_relevance":  bd.get("experience_relevance", 0),
            "education_fit":         bd.get("education_fit", 0),
            "keyword_coverage":      bd.get("keyword_coverage", 0),
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/strengths", response_model=StrengthsResponse, tags=["Analysis"],
          summary="Strengths & weaknesses",
          description="Returns strengths, weaknesses, critical gaps, and quick wins vs the JD.")
def strengths(req: StrengthsRequest, _: str = Depends(inject_api_key)):
    try:
        from agent import run_strengths_weaknesses
        return run_strengths_weaknesses(req.jd_text, req.resume_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/qa", response_model=QAResponse, tags=["Analysis"],
          summary="Q&A about JD or resume",
          description="Ask any question about the job description or resume.")
def qa(req: QARequest, _: str = Depends(inject_api_key)):
    try:
        from agent import run_qa
        answer = run_qa(req.jd_text, req.resume_text, req.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rewrite", response_model=RewriteResponse, tags=["Analysis"],
          summary="ATS-optimized resume rewrite",
          description="Rewrites the resume to maximize ATS score for the specific JD.")
def rewrite(req: RewriteRequest, _: str = Depends(inject_api_key)):
    try:
        from agent import run_rewrite
        improved = run_rewrite(req.jd_text, req.resume_text)
        return {"improved_resume": improved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/interview", response_model=InterviewResponse, tags=["Analysis"],
          summary="Interview preparation",
          description="Generates 10–12 interview questions with tailored suggested answers.")
def interview(req: InterviewRequest, _: str = Depends(inject_api_key)):
    try:
        from agent import run_interview_prep
        result = run_interview_prep(req.jd_text, req.resume_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cover-letter", response_model=CoverLetterResponse, tags=["Analysis"],
          summary="Cover letter generation",
          description="Generates a tailored cover letter matching the JD tone and requirements.")
def cover_letter(req: CoverLetterRequest, _: str = Depends(inject_api_key)):
    try:
        from agent import run_cover_letter
        letter = run_cover_letter(req.jd_text, req.resume_text)
        return {"cover_letter": letter}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Export endpoints ──────────────────────────────────────────────────────────

@app.post("/export/resume", tags=["Export"],
          summary="Export improved resume as PDF or DOCX",
          response_description="Binary file download")
def export_resume(req: ExportResumeRequest):
    try:
        from export_utils import resume_to_pdf, resume_to_docx
        if req.format == "pdf":
            data = resume_to_pdf(req.improved_resume, req.candidate_name)
            media_type = "application/pdf"
            filename = f"{req.candidate_name.replace(' ', '_')}_resume.pdf"
        else:
            data = resume_to_docx(req.improved_resume, req.candidate_name)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = f"{req.candidate_name.replace(' ', '_')}_resume.docx"

        return StreamingResponse(
            io.BytesIO(data),
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/export/cover-letter", tags=["Export"],
          summary="Export cover letter as PDF or DOCX",
          response_description="Binary file download")
def export_cover_letter(req: ExportCoverLetterRequest):
    try:
        from export_utils import cover_letter_to_pdf, cover_letter_to_docx
        if req.format == "pdf":
            data = cover_letter_to_pdf(req.cover_letter, req.candidate_name)
            media_type = "application/pdf"
            filename = f"{req.candidate_name.replace(' ', '_')}_cover_letter.pdf"
        else:
            data = cover_letter_to_docx(req.cover_letter, req.candidate_name)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = f"{req.candidate_name.replace(' ', '_')}_cover_letter.docx"

        return StreamingResponse(
            io.BytesIO(data),
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/export/interview", tags=["Export"],
          summary="Export interview prep guide as DOCX or TXT",
          response_description="Binary file download")
def export_interview(req: ExportInterviewRequest):
    try:
        from export_utils import interview_to_docx
        if req.format == "docx":
            data = interview_to_docx(req.interview_data, req.candidate_name)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = f"{req.candidate_name.replace(' ', '_')}_interview_prep.docx"
            return StreamingResponse(
                io.BytesIO(data), media_type=media_type,
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )
        else:
            questions = req.interview_data.get("questions", [])
            plain = "\n\n".join(
                f"Q{i} [{q.get('category','')}]\n{q.get('question','')}\n\n"
                f"Why asked: {q.get('why_asked','')}\n\nSuggested Answer:\n{q.get('suggested_answer','')}"
                for i, q in enumerate(questions, 1)
            )
            filename = f"{req.candidate_name.replace(' ', '_')}_interview_prep.txt"
            return StreamingResponse(
                io.BytesIO(plain.encode()),
                media_type="text/plain",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
