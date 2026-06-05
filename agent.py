"""
Resume Analyzer Agent built with LangGraph.
Nodes:
  1. fit_score       – ATS-style match score
  2. strengths_weaknesses – pros/cons vs JD
  3. qa_node         – answer questions about JD or resume
  4. resume_rewriter – generate improved resume
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
    task: Literal["score", "strengths", "qa", "rewrite"]
    question: str
    fit_score: dict
    strengths_weaknesses: dict
    qa_answer: str
    improved_resume: str
    error: str


# ── LLM ──────────────────────────────────────────────────────────────────────

def get_json_llm():
    """LLM that forces pure JSON output — no fences, no prose."""
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        google_api_key=os.environ.get("GOOGLE_API_KEY", ""),
        response_mime_type="application/json",   # ← forces raw JSON output
        convert_system_message_to_human=True,    # ← enables SystemMessage
    )

def get_text_llm():
    """LLM for free-text responses (Q&A, rewrite)."""
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        google_api_key=os.environ.get("GOOGLE_API_KEY", ""),
        convert_system_message_to_human=True,
    )


# ── Node helpers ──────────────────────────────────────────────────────────────

def _call(system: str, user: str, json_mode: bool = False) -> str:
    llm = get_json_llm() if json_mode else get_text_llm()
    msgs = [SystemMessage(content=system), HumanMessage(content=user)]
    response = llm.invoke(msgs)
    content = response.content
    if isinstance(content, list):
        content = " ".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    return content.strip()


def _parse_json(text: str) -> dict:
    """
    Robustly extract JSON object from model output.
    With json_mode=True this should always be clean JSON,
    but we keep fallbacks just in case.
    """
    # 1. Try direct parse first (clean JSON from json_mode)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Strip markdown fences (greedy to capture nested braces)
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except json.JSONDecodeError:
            pass

    # 3. Find outermost { } by counting braces
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

    graph.add_conditional_edges(
        "__start__",
        route_task,
        {
            "score": "fit_score",
            "strengths": "strengths_weaknesses",
            "qa": "qa",
            "rewrite": "resume_rewriter",
        },
    )

    graph.add_edge("fit_score", END)
    graph.add_edge("strengths_weaknesses", END)
    graph.add_edge("qa", END)
    graph.add_edge("resume_rewriter", END)

    return graph.compile()


GRAPH = build_graph()


# ── Public API ────────────────────────────────────────────────────────────────

def run_fit_score(jd: str, resume: str) -> dict:
    state = AgentState(
        jd_text=jd, resume_text=resume, task="score",
        question="", fit_score={}, strengths_weaknesses={},
        qa_answer="", improved_resume="", error=""
    )
    return GRAPH.invoke(state)["fit_score"]


def run_strengths_weaknesses(jd: str, resume: str) -> dict:
    state = AgentState(
        jd_text=jd, resume_text=resume, task="strengths",
        question="", fit_score={}, strengths_weaknesses={},
        qa_answer="", improved_resume="", error=""
    )
    return GRAPH.invoke(state)["strengths_weaknesses"]


def run_qa(jd: str, resume: str, question: str) -> str:
    state = AgentState(
        jd_text=jd, resume_text=resume, task="qa",
        question=question, fit_score={}, strengths_weaknesses={},
        qa_answer="", improved_resume="", error=""
    )
    return GRAPH.invoke(state)["qa_answer"]


def run_rewrite(jd: str, resume: str) -> str:
    state = AgentState(
        jd_text=jd, resume_text=resume, task="rewrite",
        question="", fit_score={}, strengths_weaknesses={},
        qa_answer="", improved_resume="", error=""
    )
    return GRAPH.invoke(state)["improved_resume"]