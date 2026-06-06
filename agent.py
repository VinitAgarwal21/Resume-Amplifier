"""
Resume Analyzer Agent built with LangGraph.
Nodes:
  1. fit_score             – ATS-style match score
  2. strengths_weaknesses  – pros/cons vs JD
  3. qa_node               – answer questions about JD or resume
  4. resume_rewriter       – generate improved resume
  5. interview_prep        – generate interview Q&A
  6. cover_letter          – generate tailored cover letter
"""

import os
import json
import re
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# ── State ────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    jd_text: str
    resume_text: str
    task: Literal["score", "strengths", "qa", "rewrite", "interview", "cover_letter"]
    question: str
    fit_score: dict
    strengths_weaknesses: dict
    qa_answer: str
    improved_resume: str
    interview_prep: dict       # {"questions": [{"question":..,"answer":..,"category":..}]}
    cover_letter: str
    error: str


# ── LLM ──────────────────────────────────────────────────────────────────────

def get_json_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        google_api_key=os.environ.get("GOOGLE_API_KEY", ""),
        response_mime_type="application/json",
        convert_system_message_to_human=True,
    )

def get_text_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        google_api_key=os.environ.get("GOOGLE_API_KEY", ""),
        convert_system_message_to_human=True,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _call(system: str, user: str, json_mode: bool = False) -> str:
    llm = get_json_llm() if json_mode else get_text_llm()
    msgs = [SystemMessage(content=system), HumanMessage(content=user)]
    response = llm.invoke(msgs)
    content = response.content
    if isinstance(content, list):
        content = " ".join(
            block.get("text", "") if isinstance(block, dict) else str(block) for block in content
        )
    return content.strip()


def _parse_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except json.JSONDecodeError:
            pass
    start = text.find("{")
    if start != -1:
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i+1])
                    except json.JSONDecodeError:
                        break
    return {}


# ── Nodes ─────────────────────────────────────────────────────────────────────

def fit_score_node(state: AgentState) -> AgentState:
    system = """You are an expert ATS (Applicant Tracking System) and senior technical recruiter.
Analyze how well a resume matches a job description.
Return a JSON object with exactly these keys:
- score: integer 0-100
- label: one of "Poor", "Fair", "Good", "Excellent"
- summary: 2-3 sentence overall assessment string
- breakdown: object with keys skills_match, experience_relevance, education_fit, keyword_coverage (each integer 0-100)
- matched_keywords: array of keyword strings found in both JD and resume
- missing_keywords: array of keyword strings in JD but absent from resume"""

    user = f"JOB DESCRIPTION:\n{state['jd_text']}\n\nRESUME:\n{state['resume_text']}"
    raw = _call(system, user, json_mode=True)
    parsed = _parse_json(raw)
    if not parsed:
        parsed = {
            "score": 0, "label": "Error",
            "summary": f"Parse failed. Raw output: {raw[:300]}",
            "breakdown": {}, "matched_keywords": [], "missing_keywords": []
        }
    return {**state, "fit_score": parsed}


def strengths_weaknesses_node(state: AgentState) -> AgentState:
    system = """You are a senior career coach and technical recruiter.
Analyze the resume against the job description and return a JSON object with exactly these keys:
- strengths: array of objects, each with keys "title" (string) and "detail" (string)
- weaknesses: array of objects, each with keys "title" (string), "detail" (string), "suggestion" (string)
- critical_gaps: array of strings listing the most important missing qualifications
- quick_wins: array of strings listing easy improvements the candidate can make immediately
Provide 4-6 items in each of strengths and weaknesses."""

    user = f"JOB DESCRIPTION:\n{state['jd_text']}\n\nRESUME:\n{state['resume_text']}"
    raw = _call(system, user, json_mode=True)
    parsed = _parse_json(raw)
    if not parsed:
        parsed = {"strengths": [], "weaknesses": [], "critical_gaps": [], "quick_wins": []}
    return {**state, "strengths_weaknesses": parsed}


def qa_node(state: AgentState) -> AgentState:
    system = """You are a helpful career advisor with deep knowledge of the provided job description and resume.
Answer the user's question accurately and concisely based solely on the provided documents.
If the answer cannot be found in the documents, say so clearly.
Format your answer in clear paragraphs. Use bullet points only when listing multiple items."""

    user = (
        f"JOB DESCRIPTION:\n{state['jd_text']}\n\n"
        f"RESUME:\n{state['resume_text']}\n\n"
        f"QUESTION: {state['question']}"
    )
    answer = _call(system, user, json_mode=False)
    return {**state, "qa_answer": answer}


def resume_rewriter_node(state: AgentState) -> AgentState:
    system = """You are an expert resume writer specializing in ATS optimization.
Rewrite the provided resume to maximize its chances of passing ATS screening for the specific job description.
Rules:
- Keep all facts truthful — do NOT fabricate experiences or skills
- Incorporate relevant keywords from the JD naturally
- Strengthen action verbs and quantify achievements where possible
- Use ALL CAPS section headers (SUMMARY, EXPERIENCE, EDUCATION, SKILLS, etc.)
Output ONLY the improved resume as plain text — no commentary, no explanation."""

    user = f"JOB DESCRIPTION:\n{state['jd_text']}\n\nORIGINAL RESUME:\n{state['resume_text']}"
    improved = _call(system, user, json_mode=False)
    return {**state, "improved_resume": improved}


def interview_prep_node(state: AgentState) -> AgentState:
    system = """You are an expert interview coach and hiring manager.
Based on the job description and candidate's resume, generate realistic interview questions
the candidate is likely to face, along with strong suggested answers tailored to their background.

Return a JSON object with exactly this structure:
{
  "questions": [
    {
      "category": "<Behavioral|Technical|Situational|Role-Specific|Culture Fit>",
      "question": "...",
      "why_asked": "one sentence on why interviewers ask this",
      "suggested_answer": "a strong 3-5 sentence answer drawing from the resume"
    }
  ]
}
Generate 10-12 questions spread across categories."""

    user = f"JOB DESCRIPTION:\n{state['jd_text']}\n\nRESUME:\n{state['resume_text']}"
    raw = _call(system, user, json_mode=True)
    parsed = _parse_json(raw)
    if not parsed:
        parsed = {"questions": []}
    return {**state, "interview_prep": parsed}


def cover_letter_node(state: AgentState) -> AgentState:
    system = """You are an expert career coach and professional writer.
Write a compelling, tailored cover letter for the candidate applying to the role in the job description.

Rules:
- Match the tone and language of the job description
- Open with a strong hook — not "I am applying for..."
- Highlight 2-3 specific achievements from the resume most relevant to the JD
- Show genuine enthusiasm for the company/role without being generic
- Close with a confident call to action
- Keep it to 3-4 paragraphs, under 400 words
- Do NOT fabricate any information not present in the resume
- Output ONLY the cover letter text — no subject line, no commentary"""

    user = f"JOB DESCRIPTION:\n{state['jd_text']}\n\nRESUME:\n{state['resume_text']}"
    letter = _call(system, user, json_mode=False)
    return {**state, "cover_letter": letter}


# ── Router ────────────────────────────────────────────────────────────────────

def route_task(state: AgentState) -> str:
    return state["task"]


# ── Build Graph ───────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("fit_score", fit_score_node)
    graph.add_node("strengths_weaknesses", strengths_weaknesses_node)
    graph.add_node("qa", qa_node)
    graph.add_node("resume_rewriter", resume_rewriter_node)
    graph.add_node("interview_prep", interview_prep_node)
    graph.add_node("cover_letter", cover_letter_node)

    graph.add_conditional_edges(
        "__start__",
        route_task,
        {
            "score": "fit_score",
            "strengths": "strengths_weaknesses",
            "qa": "qa",
            "rewrite": "resume_rewriter",
            "interview": "interview_prep",
            "cover_letter": "cover_letter",
        },
    )

    for node in ["fit_score", "strengths_weaknesses", "qa",
                 "resume_rewriter", "interview_prep", "cover_letter"]:
        graph.add_edge(node, END)

    return graph.compile()


GRAPH = build_graph()


# ── Public API ────────────────────────────────────────────────────────────────

def _base_state(jd, resume, task, **kwargs):
    return AgentState(
        jd_text=jd, resume_text=resume, task=task,
        question=kwargs.get("question", ""),
        fit_score={}, strengths_weaknesses={},
        qa_answer="", improved_resume="",
        interview_prep={}, cover_letter="", error=""
    )

def run_fit_score(jd: str, resume: str) -> dict:
    return GRAPH.invoke(_base_state(jd, resume, "score"))["fit_score"]

def run_strengths_weaknesses(jd: str, resume: str) -> dict:
    return GRAPH.invoke(_base_state(jd, resume, "strengths"))["strengths_weaknesses"]

def run_qa(jd: str, resume: str, question: str) -> str:
    return GRAPH.invoke(_base_state(jd, resume, "qa", question=question))["qa_answer"]

def run_rewrite(jd: str, resume: str) -> str:
    return GRAPH.invoke(_base_state(jd, resume, "rewrite"))["improved_resume"]

def run_interview_prep(jd: str, resume: str) -> dict:
    return GRAPH.invoke(_base_state(jd, resume, "interview"))["interview_prep"]

def run_cover_letter(jd: str, resume: str) -> str:
    return GRAPH.invoke(_base_state(jd, resume, "cover_letter"))["cover_letter"]