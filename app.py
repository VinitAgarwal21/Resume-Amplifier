"""
Resume Analyzer — Streamlit Frontend
Run:  streamlit run app.py
"""

import streamlit as st
import io
import os
import tempfile

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Resume Analyzer AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #12121a;
    --surface2: #1a1a26;
    --border: #2a2a3d;
    --accent: #6366f1;
    --accent2: #8b5cf6;
    --green: #10b981;
    --red: #ef4444;
    --amber: #f59e0b;
    --text: #e2e8f0;
    --muted: #94a3b8;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    color: var(--text) !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 24px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    width: 100% !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4) !important;
}

.stTextArea textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
}

.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1px solid var(--border) !important;
}

.stTabs [data-baseweb="tab"] {
    color: var(--muted) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: white !important;
}

[data-testid="stFileUploader"] {
    background: var(--surface2) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
}

.stProgress > div > div {
    background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
}

.stAlert {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
}

.metric-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: border-color 0.2s;
}

.metric-card:hover {
    border-color: var(--accent);
}

.score-ring {
    font-size: 52px;
    font-weight: 700;
    font-family: 'Space Grotesk', sans-serif;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-green { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }
.badge-amber { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
.badge-red   { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid rgba(239,68,68,0.3);  }
.badge-blue  { background: rgba(99,102,241,0.15); color: #818cf8; border: 1px solid rgba(99,102,241,0.3); }

.strength-item {
    background: rgba(16,185,129,0.06);
    border: 1px solid rgba(16,185,129,0.2);
    border-left: 3px solid #10b981;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
}

.weakness-item {
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.2);
    border-left: 3px solid #ef4444;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
}

.suggestion-pill {
    display: inline-block;
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.25);
    color: #818cf8;
    font-size: 12px;
    padding: 3px 10px;
    border-radius: 12px;
    margin-top: 6px;
}

.chat-bubble-user {
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.15));
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 12px 12px 4px 12px;
    padding: 14px 18px;
    margin-bottom: 16px;
    text-align: right;
}

.chat-bubble-ai {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px 12px 12px 4px;
    padding: 14px 18px;
    margin-bottom: 16px;
    line-height: 1.7;
}

.resume-output {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px 28px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    line-height: 1.8;
    white-space: pre-wrap;
    max-height: 600px;
    overflow-y: auto;
}

.section-header {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--muted);
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
}

.keyword-chip {
    display: inline-block;
    margin: 3px;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
}

.keyword-match { background: rgba(16,185,129,0.12); color: #10b981; border: 1px solid rgba(16,185,129,0.25); }
.keyword-miss  { background: rgba(239,68,68,0.12);  color: #ef4444; border: 1px solid rgba(239,68,68,0.25); }

.stSelectbox > div { background: var(--surface2) !important; border-color: var(--border) !important; }
.stSelectbox label { color: var(--muted) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text) !important; }

/* hide streamlit chrome */
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Utilities ─────────────────────────────────────────────────────────────────

def extract_text_from_file(uploaded_file) -> str:
    """Extract plain text from .txt, .pdf, or .docx uploads."""
    name = uploaded_file.name.lower()
    if name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")

    if name.endswith(".pdf"):
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            return "\n".join(p.extract_text() or "" for p in reader.pages)
        except Exception as e:
            return f"[PDF extraction error: {e}]"

    if name.endswith(".docx"):
        try:
            from docx import Document
            doc = Document(io.BytesIO(uploaded_file.read()))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as e:
            return f"[DOCX extraction error: {e}]"

    return uploaded_file.read().decode("utf-8", errors="ignore")


def score_color(score: int) -> str:
    if score >= 75: return "green"
    if score >= 50: return "amber"
    return "red"


def score_label_color(label: str) -> str:
    mapping = {"Excellent": "green", "Good": "green", "Fair": "amber", "Poor": "red"}
    return mapping.get(label, "blue")


# ── Session state ──────────────────────────────────────────────────────────────

for key in ["jd_text", "resume_text", "fit_result", "sw_result", "improved_resume", "chat_history"]:
    if key not in st.session_state:
        st.session_state[key] = None if key not in ["chat_history"] else []


# ── Sidebar: Input panel ───────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🎯 Resume Analyzer")
    st.markdown('<p style="color:#94a3b8;font-size:13px;margin-top:-8px;">Powered by LangGraph + Gemini</p>', unsafe_allow_html=True)
    st.divider()

    # API Key
    api_key = st.text_input(
        "🔑 Google API Key",
        type="password",
        placeholder="AIza...",
        help="Free at aistudio.google.com/apikey — used only for this session.",
    )
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

    st.markdown("---")
    st.markdown('<div class="section-header">Job Description</div>', unsafe_allow_html=True)

    jd_mode = st.radio("Input method", ["Paste text", "Upload file"], key="jd_mode", horizontal=True, label_visibility="collapsed")

    if jd_mode == "Paste text":
        jd_input = st.text_area("Job Description", height=180, placeholder="Paste the full job description here...", label_visibility="collapsed")
        if jd_input:
            st.session_state.jd_text = jd_input
    else:
        jd_file = st.file_uploader("Upload JD", type=["txt", "pdf", "docx"], label_visibility="collapsed", key="jd_file")
        if jd_file:
            st.session_state.jd_text = extract_text_from_file(jd_file)
            st.success(f"✓ {jd_file.name} loaded")

    st.markdown("---")
    st.markdown('<div class="section-header">Resume</div>', unsafe_allow_html=True)

    res_mode = st.radio("Input method", ["Paste text", "Upload file"], key="res_mode", horizontal=True, label_visibility="collapsed")

    if res_mode == "Paste text":
        res_input = st.text_area("Resume", height=180, placeholder="Paste your resume here...", label_visibility="collapsed")
        if res_input:
            st.session_state.resume_text = res_input
    else:
        res_file = st.file_uploader("Upload Resume", type=["txt", "pdf", "docx"], label_visibility="collapsed", key="res_file")
        if res_file:
            st.session_state.resume_text = extract_text_from_file(res_file)
            st.success(f"✓ {res_file.name} loaded")

    # Status indicators
    st.markdown("---")
    jd_ok  = bool(st.session_state.jd_text)
    res_ok = bool(st.session_state.resume_text)
    key_ok = bool(api_key)

    col1, col2 = st.columns(2)
    col1.markdown(f"{'✅' if jd_ok  else '⬜'} JD")
    col2.markdown(f"{'✅' if res_ok else '⬜'} Resume")
    if not key_ok:
        st.warning("⚠️ Add your Google API key above to begin.", icon=None)


# ── Main area ─────────────────────────────────────────────────────────────────

st.markdown("""
<div style="margin-bottom:24px;">
  <h1 style="font-size:2rem;margin-bottom:4px;">Resume Intelligence Suite</h1>
  <p style="color:#94a3b8;font-size:15px;">Upload your JD & resume in the sidebar, then explore each tab.</p>
</div>
""", unsafe_allow_html=True)

ready = jd_ok and res_ok and key_ok

tab1, tab2, tab3, tab4 = st.tabs(["📊 Fit Score", "💪 Strengths & Weaknesses", "💬 Q&A", "✨ Improved Resume"])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 – FIT SCORE
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    if not ready:
        st.info("👈 Add your JD, resume, and API key in the sidebar to get started.")
    else:
        if st.button("🔍 Analyze Fit", key="btn_score"):
            with st.spinner("Running ATS analysis via LangGraph…"):
                try:
                    from agent import run_fit_score
                    st.session_state.fit_result = run_fit_score(
                        st.session_state.jd_text,
                        st.session_state.resume_text
                    )
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.fit_result:
            r = st.session_state.fit_result
            score = r.get("score", 0)
            label = r.get("label", "—")
            color = score_color(score)
            lc    = score_label_color(label)

            # Big score display
            st.markdown(f"""
            <div style="text-align:center;padding:32px 0 24px;">
              <div class="score-ring">{score}<span style="font-size:24px;font-weight:400">%</span></div>
              <br/>
              <span class="badge badge-{lc}">{label} Match</span>
              <p style="color:#94a3b8;margin-top:16px;font-size:14px;max-width:600px;margin-left:auto;margin-right:auto;">
                {r.get('summary','')}
              </p>
            </div>
            """, unsafe_allow_html=True)

            # Progress bar
            st.progress(score / 100)

            # Breakdown metrics
            bd = r.get("breakdown", {})
            if bd:
                st.markdown("#### Score Breakdown")
                cols = st.columns(len(bd))
                labels = {
                    "skills_match": "Skills Match",
                    "experience_relevance": "Experience",
                    "education_fit": "Education",
                    "keyword_coverage": "Keywords"
                }
                for col, (k, v) in zip(cols, bd.items()):
                    with col:
                        st.markdown(f"""
                        <div class="metric-card">
                          <div style="font-size:28px;font-weight:700;color:{'#10b981' if v>=70 else '#f59e0b' if v>=45 else '#ef4444'}">{v}</div>
                          <div style="font-size:12px;color:#94a3b8;margin-top:4px;">{labels.get(k, k.replace('_',' ').title())}</div>
                        </div>
                        """, unsafe_allow_html=True)

            # Keywords
            col_a, col_b = st.columns(2)
            with col_a:
                matched = r.get("matched_keywords", [])
                if matched:
                    st.markdown("**✅ Matched Keywords**")
                    st.markdown(" ".join(f'<span class="keyword-chip keyword-match">{kw}</span>' for kw in matched), unsafe_allow_html=True)

            with col_b:
                missing = r.get("missing_keywords", [])
                if missing:
                    st.markdown("**❌ Missing Keywords**")
                    st.markdown(" ".join(f'<span class="keyword-chip keyword-miss">{kw}</span>' for kw in missing), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 – STRENGTHS & WEAKNESSES
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    if not ready:
        st.info("👈 Add your JD, resume, and API key in the sidebar to get started.")
    else:
        if st.button("🔎 Analyze Strengths & Weaknesses", key="btn_sw"):
            with st.spinner("Evaluating your resume against the JD…"):
                try:
                    from agent import run_strengths_weaknesses
                    st.session_state.sw_result = run_strengths_weaknesses(
                        st.session_state.jd_text,
                        st.session_state.resume_text
                    )
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.sw_result:
            sw = st.session_state.sw_result
            col_s, col_w = st.columns(2)

            with col_s:
                st.markdown("### 💚 Strengths")
                for item in sw.get("strengths", []):
                    st.markdown(f"""
                    <div class="strength-item">
                      <strong>{item.get('title','')}</strong>
                      <p style="margin:6px 0 0;font-size:14px;color:#cbd5e1;">{item.get('detail','')}</p>
                    </div>
                    """, unsafe_allow_html=True)

            with col_w:
                st.markdown("### 🔴 Weaknesses")
                for item in sw.get("weaknesses", []):
                    st.markdown(f"""
                    <div class="weakness-item">
                      <strong>{item.get('title','')}</strong>
                      <p style="margin:6px 0 0;font-size:14px;color:#cbd5e1;">{item.get('detail','')}</p>
                      {'<span class="suggestion-pill">💡 ' + item.get("suggestion","") + '</span>' if item.get("suggestion") else ''}
                    </div>
                    """, unsafe_allow_html=True)

            # Critical gaps & quick wins
            col_g, col_q = st.columns(2)
            with col_g:
                gaps = sw.get("critical_gaps", [])
                if gaps:
                    st.markdown("#### 🚨 Critical Gaps")
                    for g in gaps:
                        st.markdown(f"- {g}")

            with col_q:
                wins = sw.get("quick_wins", [])
                if wins:
                    st.markdown("#### ⚡ Quick Wins")
                    for w in wins:
                        st.markdown(f"- {w}")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 – Q&A
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    if not ready:
        st.info("👈 Add your JD, resume, and API key in the sidebar to get started.")
    else:
        st.markdown("Ask anything about the job description or your resume.")

        # Suggested questions
        suggested = [
            "What are the top 3 required skills I'm missing?",
            "Does my experience level match this role?",
            "What technologies mentioned in the JD am I not proficient in?",
            "How many years of experience does this role require?",
            "What soft skills does the JD emphasize?",
        ]
        st.markdown("**💡 Suggested questions:**")
        scols = st.columns(3)
        for i, q in enumerate(suggested):
            if scols[i % 3].button(q, key=f"sq_{i}", use_container_width=True):
                st.session_state["prefill_q"] = q

        # Chat display
        for turn in st.session_state.chat_history:
            st.markdown(f'<div class="chat-bubble-user">🧑 {turn["q"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-bubble-ai">🤖 {turn["a"]}</div>', unsafe_allow_html=True)

        # Input
        prefill = st.session_state.pop("prefill_q", "")
        question = st.text_input("Your question", value=prefill, placeholder="e.g. What skills am I missing for this role?", key="qa_input")

        col_ask, col_clear = st.columns([4, 1])
        with col_ask:
            ask_btn = st.button("Ask →", key="btn_ask", use_container_width=True)
        with col_clear:
            if st.button("Clear", key="btn_clear", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

        if ask_btn and question.strip():
            with st.spinner("Thinking…"):
                try:
                    from agent import run_qa
                    answer = run_qa(
                        st.session_state.jd_text,
                        st.session_state.resume_text,
                        question.strip()
                    )
                    st.session_state.chat_history.append({"q": question.strip(), "a": answer})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 – IMPROVED RESUME
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    if not ready:
        st.info("👈 Add your JD, resume, and API key in the sidebar to get started.")
    else:
        st.markdown("Generate a tailored, ATS-optimized version of your resume for this specific JD.")
        st.caption("ℹ️ No information is fabricated — only existing content is rewritten and reorganized.")

        if st.button("✨ Generate Improved Resume", key="btn_rewrite"):
            with st.spinner("Rewriting your resume for maximum impact…"):
                try:
                    from agent import run_rewrite
                    st.session_state.improved_resume = run_rewrite(
                        st.session_state.jd_text,
                        st.session_state.resume_text
                    )
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.improved_resume:
            col_orig, col_new = st.columns(2)
            with col_orig:
                st.markdown("#### 📄 Original Resume")
                st.markdown(f'<div class="resume-output">{st.session_state.resume_text}</div>', unsafe_allow_html=True)

            with col_new:
                st.markdown("#### ✨ Improved Resume")
                st.markdown(f'<div class="resume-output">{st.session_state.improved_resume}</div>', unsafe_allow_html=True)

            # Download button
            st.download_button(
                label="⬇️ Download Improved Resume (.txt)",
                data=st.session_state.improved_resume,
                file_name="improved_resume.txt",
                mime="text/plain",
                use_container_width=True,
            )