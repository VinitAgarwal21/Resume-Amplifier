"""
Resume Analyzer — Streamlit Frontend
Run:  streamlit run app.py
"""

import streamlit as st
import io
import os

st.set_page_config(
    page_title="Resume Analyzer AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
    --bg:#0a0a0f; --surface:#12121a; --surface2:#1a1a26; --border:#2a2a3d;
    --accent:#6366f1; --accent2:#8b5cf6; --green:#10b981; --red:#ef4444;
    --amber:#f59e0b; --text:#e2e8f0; --muted:#94a3b8;
}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text)!important;font-family:'Space Grotesk',sans-serif!important;}
[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border)!important;}
[data-testid="stSidebar"] *{color:var(--text)!important;}
h1,h2,h3,h4{font-family:'Space Grotesk',sans-serif!important;font-weight:700!important;color:var(--text)!important;}
.stButton>button{background:linear-gradient(135deg,var(--accent),var(--accent2))!important;color:white!important;border:none!important;border-radius:8px!important;font-family:'Space Grotesk',sans-serif!important;font-weight:600!important;font-size:14px!important;padding:10px 24px!important;width:100%!important;transition:all 0.2s!important;}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 8px 25px rgba(99,102,241,0.4)!important;}
.stTextArea textarea{background:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:8px!important;color:var(--text)!important;font-family:'JetBrains Mono',monospace!important;font-size:13px!important;}
.stTextArea textarea:focus{border-color:var(--accent)!important;box-shadow:0 0 0 2px rgba(99,102,241,0.2)!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--surface)!important;border-radius:10px!important;padding:4px!important;border:1px solid var(--border)!important;}
.stTabs [data-baseweb="tab"]{color:var(--muted)!important;font-family:'Space Grotesk',sans-serif!important;font-weight:500!important;border-radius:8px!important;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,var(--accent),var(--accent2))!important;color:white!important;}
[data-testid="stFileUploader"]{background:var(--surface2)!important;border:2px dashed var(--border)!important;border-radius:12px!important;}
.stProgress>div>div{background:linear-gradient(90deg,var(--accent),var(--accent2))!important;}
.metric-card{background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:20px;text-align:center;transition:border-color 0.2s;}
.metric-card:hover{border-color:var(--accent);}
.score-ring{font-size:52px;font-weight:700;font-family:'Space Grotesk',sans-serif;background:linear-gradient(135deg,#6366f1,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;}
.badge-green{background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.3);}
.badge-amber{background:rgba(245,158,11,0.15);color:#f59e0b;border:1px solid rgba(245,158,11,0.3);}
.badge-red{background:rgba(239,68,68,0.15);color:#ef4444;border:1px solid rgba(239,68,68,0.3);}
.badge-blue{background:rgba(99,102,241,0.15);color:#818cf8;border:1px solid rgba(99,102,241,0.3);}
.strength-item{background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.2);border-left:3px solid #10b981;border-radius:8px;padding:14px 18px;margin-bottom:10px;}
.weakness-item{background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.2);border-left:3px solid #ef4444;border-radius:8px;padding:14px 18px;margin-bottom:10px;}
.suggestion-pill{display:inline-block;background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.25);color:#818cf8;font-size:12px;padding:3px 10px;border-radius:12px;margin-top:6px;}
.chat-bubble-user{background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(139,92,246,0.15));border:1px solid rgba(99,102,241,0.3);border-radius:12px 12px 4px 12px;padding:14px 18px;margin-bottom:16px;text-align:right;}
.chat-bubble-ai{background:var(--surface2);border:1px solid var(--border);border-radius:12px 12px 12px 4px;padding:14px 18px;margin-bottom:16px;line-height:1.7;}
.resume-output{background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:24px 28px;font-family:'JetBrains Mono',monospace;font-size:13px;line-height:1.8;white-space:pre-wrap;max-height:600px;overflow-y:auto;}
.cover-letter-output{background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:28px 32px;font-family:'Space Grotesk',sans-serif;font-size:14px;line-height:1.9;max-height:600px;overflow-y:auto;}
.section-header{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:2px;color:var(--muted);margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid var(--border);}
.keyword-chip{display:inline-block;margin:3px;padding:4px 10px;border-radius:6px;font-size:12px;font-weight:500;}
.keyword-match{background:rgba(16,185,129,0.12);color:#10b981;border:1px solid rgba(16,185,129,0.25);}
.keyword-miss{background:rgba(239,68,68,0.12);color:#ef4444;border:1px solid rgba(239,68,68,0.25);}
.q-card{background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:20px 24px;margin-bottom:16px;transition:border-color 0.2s;}
.q-card:hover{border-color:var(--accent);}
.q-card-header{display:flex;align-items:center;gap:10px;margin-bottom:10px;}
.q-number{background:linear-gradient(135deg,var(--accent),var(--accent2));color:white;border-radius:6px;padding:2px 10px;font-size:12px;font-weight:700;}
.q-category{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px;color:var(--muted);}
.q-text{font-size:15px;font-weight:600;color:var(--text);margin-bottom:10px;}
.q-why{font-size:12px;color:var(--muted);font-style:italic;margin-bottom:10px;padding:8px 12px;background:rgba(99,102,241,0.06);border-radius:6px;}
.q-answer{font-size:13px;color:#cbd5e1;line-height:1.7;padding:12px 16px;background:rgba(16,185,129,0.05);border-left:3px solid var(--green);border-radius:0 8px 8px 0;}
[data-testid="stMarkdownContainer"] p{color:var(--text)!important;}
#MainMenu,footer,[data-testid="stToolbar"]{visibility:hidden;}
</style>
""", unsafe_allow_html=True)


# ── Utilities ─────────────────────────────────────────────────────────────────

def extract_text_from_file(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    if name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")
    if name.endswith(".pdf"):
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            return "\n".join(p.extract_text() or "" for p in reader.pages)
        except Exception as e:
            return f"[PDF error: {e}]"
    if name.endswith(".docx"):
        try:
            from docx import Document
            doc = Document(io.BytesIO(uploaded_file.read()))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as e:
            return f"[DOCX error: {e}]"
    return uploaded_file.read().decode("utf-8", errors="ignore")

def score_color(s): return "green" if s>=75 else "amber" if s>=50 else "red"
def score_label_color(l): return {"Excellent":"green","Good":"green","Fair":"amber","Poor":"red"}.get(l,"blue")

CATEGORY_COLORS = {
    "Behavioral":    "#f59e0b",
    "Technical":     "#6366f1",
    "Situational":   "#10b981",
    "Role-Specific": "#ec4899",
    "Culture Fit":   "#14b8a6",
}

# ── Session state ──────────────────────────────────────────────────────────────

for key, default in [
    ("jd_text", None), ("resume_text", None),
    ("fit_result", None), ("sw_result", None),
    ("improved_resume", None), ("chat_history", []),
    ("interview_result", None), ("cover_letter", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🎯 Resume Analyzer")
    st.markdown('<p style="color:#94a3b8;font-size:13px;margin-top:-8px;">Powered by LangGraph + Gemini</p>', unsafe_allow_html=True)
    st.divider()

    api_key = st.text_input("🔑 Google API Key", type="password", placeholder="AIza...",
                             help="Free at aistudio.google.com/apikey")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

    st.markdown("---")
    st.markdown('<div class="section-header">Job Description</div>', unsafe_allow_html=True)
    jd_mode = st.radio("JD input", ["Paste text","Upload file"], key="jd_mode", horizontal=True, label_visibility="collapsed")
    if jd_mode == "Paste text":
        jd_input = st.text_area("JD", height=160, placeholder="Paste job description…", label_visibility="collapsed")
        if jd_input: st.session_state.jd_text = jd_input
    else:
        jd_file = st.file_uploader("JD file", type=["txt","pdf","docx"], label_visibility="collapsed", key="jd_file")
        if jd_file:
            st.session_state.jd_text = extract_text_from_file(jd_file)
            st.success(f"✓ {jd_file.name}")

    st.markdown("---")
    st.markdown('<div class="section-header">Resume</div>', unsafe_allow_html=True)
    res_mode = st.radio("Resume input", ["Paste text","Upload file"], key="res_mode", horizontal=True, label_visibility="collapsed")
    if res_mode == "Paste text":
        res_input = st.text_area("Resume", height=160, placeholder="Paste resume…", label_visibility="collapsed")
        if res_input: st.session_state.resume_text = res_input
    else:
        res_file = st.file_uploader("Resume file", type=["txt","pdf","docx"], label_visibility="collapsed", key="res_file")
        if res_file:
            st.session_state.resume_text = extract_text_from_file(res_file)
            st.success(f"✓ {res_file.name}")

    st.markdown("---")
    jd_ok  = bool(st.session_state.jd_text)
    res_ok = bool(st.session_state.resume_text)
    key_ok = bool(api_key)
    c1, c2 = st.columns(2)
    c1.markdown(f"{'✅' if jd_ok else '⬜'} JD")
    c2.markdown(f"{'✅' if res_ok else '⬜'} Resume")
    if not key_ok:
        st.warning("⚠️ Add your Google API key to begin.")


# ── Main ──────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="margin-bottom:24px;">
  <h1 style="font-size:2rem;margin-bottom:4px;">Resume Intelligence Suite</h1>
  <p style="color:#94a3b8;font-size:15px;">Upload your JD & resume in the sidebar, then explore each tab.</p>
</div>
""", unsafe_allow_html=True)

ready = jd_ok and res_ok and key_ok

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Fit Score",
    "💪 Strengths & Weaknesses",
    "💬 Q&A",
    "✨ Improved Resume",
    "🎤 Interview Prep",
    "✉️ Cover Letter",
    "📥 Export",
])


# ── TAB 1: FIT SCORE ──────────────────────────────────────────────────────────
with tab1:
    if not ready:
        st.info("👈 Add your JD, resume, and API key in the sidebar to get started.")
    else:
        if st.button("🔍 Analyze Fit", key="btn_score"):
            with st.spinner("Running ATS analysis…"):
                try:
                    from agent import run_fit_score
                    st.session_state.fit_result = run_fit_score(st.session_state.jd_text, st.session_state.resume_text)
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.fit_result:
            r = st.session_state.fit_result
            score = r.get("score", 0)
            label = r.get("label", "—")
            lc = score_label_color(label)
            st.markdown(f"""
            <div style="text-align:center;padding:32px 0 24px;">
              <div class="score-ring">{score}<span style="font-size:24px;font-weight:400">%</span></div><br/>
              <span class="badge badge-{lc}">{label} Match</span>
              <p style="color:#94a3b8;margin-top:16px;font-size:14px;max-width:600px;margin:16px auto 0;">
                {r.get('summary','')}
              </p>
            </div>""", unsafe_allow_html=True)
            st.progress(score / 100)

            bd = r.get("breakdown", {})
            if bd:
                st.markdown("#### Score Breakdown")
                labels = {"skills_match":"Skills Match","experience_relevance":"Experience","education_fit":"Education","keyword_coverage":"Keywords"}
                cols = st.columns(len(bd))
                for col, (k, v) in zip(cols, bd.items()):
                    with col:
                        st.markdown(f"""<div class="metric-card">
                          <div style="font-size:28px;font-weight:700;color:{'#10b981' if v>=70 else '#f59e0b' if v>=45 else '#ef4444'}">{v}</div>
                          <div style="font-size:12px;color:#94a3b8;margin-top:4px;">{labels.get(k,k)}</div>
                        </div>""", unsafe_allow_html=True)

            ca, cb = st.columns(2)
            with ca:
                matched = r.get("matched_keywords", [])
                if matched:
                    st.markdown("**✅ Matched Keywords**")
                    st.markdown(" ".join(f'<span class="keyword-chip keyword-match">{kw}</span>' for kw in matched), unsafe_allow_html=True)
            with cb:
                missing = r.get("missing_keywords", [])
                if missing:
                    st.markdown("**❌ Missing Keywords**")
                    st.markdown(" ".join(f'<span class="keyword-chip keyword-miss">{kw}</span>' for kw in missing), unsafe_allow_html=True)


# ── TAB 2: STRENGTHS & WEAKNESSES ─────────────────────────────────────────────
with tab2:
    if not ready:
        st.info("👈 Add your JD, resume, and API key in the sidebar to get started.")
    else:
        if st.button("🔎 Analyze Strengths & Weaknesses", key="btn_sw"):
            with st.spinner("Evaluating your resume against the JD…"):
                try:
                    from agent import run_strengths_weaknesses
                    st.session_state.sw_result = run_strengths_weaknesses(st.session_state.jd_text, st.session_state.resume_text)
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.sw_result:
            sw = st.session_state.sw_result
            cs, cw = st.columns(2)
            with cs:
                st.markdown("### 💚 Strengths")
                for item in sw.get("strengths", []):
                    st.markdown(f"""<div class="strength-item">
                      <strong>{item.get('title','')}</strong>
                      <p style="margin:6px 0 0;font-size:14px;color:#cbd5e1;">{item.get('detail','')}</p>
                    </div>""", unsafe_allow_html=True)
            with cw:
                st.markdown("### 🔴 Weaknesses")
                for item in sw.get("weaknesses", []):
                    st.markdown(f"""<div class="weakness-item">
                      <strong>{item.get('title','')}</strong>
                      <p style="margin:6px 0 0;font-size:14px;color:#cbd5e1;">{item.get('detail','')}</p>
                      {'<span class="suggestion-pill">💡 '+item.get("suggestion","")+'</span>' if item.get("suggestion") else ''}
                    </div>""", unsafe_allow_html=True)

            cg, cq = st.columns(2)
            with cg:
                gaps = sw.get("critical_gaps", [])
                if gaps:
                    st.markdown("#### 🚨 Critical Gaps")
                    for g in gaps: st.markdown(f"- {g}")
            with cq:
                wins = sw.get("quick_wins", [])
                if wins:
                    st.markdown("#### ⚡ Quick Wins")
                    for w in wins: st.markdown(f"- {w}")


# ── TAB 3: Q&A ────────────────────────────────────────────────────────────────
with tab3:
    if not ready:
        st.info("👈 Add your JD, resume, and API key in the sidebar to get started.")
    else:
        st.markdown("Ask anything about the job description or your resume.")
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

        for turn in st.session_state.chat_history:
            st.markdown(f'<div class="chat-bubble-user">🧑 {turn["q"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-bubble-ai">🤖 {turn["a"]}</div>', unsafe_allow_html=True)

        prefill = st.session_state.pop("prefill_q", "")
        question = st.text_input("Your question", value=prefill, placeholder="e.g. What skills am I missing?", key="qa_input")
        ca2, cc2 = st.columns([4, 1])
        with ca2: ask_btn = st.button("Ask →", key="btn_ask", use_container_width=True)
        with cc2:
            if st.button("Clear", key="btn_clear", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

        if ask_btn and question.strip():
            with st.spinner("Thinking…"):
                try:
                    from agent import run_qa
                    answer = run_qa(st.session_state.jd_text, st.session_state.resume_text, question.strip())
                    st.session_state.chat_history.append({"q": question.strip(), "a": answer})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")


# ── TAB 4: IMPROVED RESUME ────────────────────────────────────────────────────
with tab4:
    if not ready:
        st.info("👈 Add your JD, resume, and API key in the sidebar to get started.")
    else:
        st.markdown("Generate a tailored, ATS-optimized version of your resume.")
        st.caption("ℹ️ No information is fabricated — only existing content is rewritten and reorganized.")

        if st.button("✨ Generate Improved Resume", key="btn_rewrite"):
            with st.spinner("Rewriting your resume for maximum impact…"):
                try:
                    from agent import run_rewrite
                    st.session_state.improved_resume = run_rewrite(st.session_state.jd_text, st.session_state.resume_text)
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.improved_resume:
            co, cn = st.columns(2)
            with co:
                st.markdown("#### 📄 Original")
                st.markdown(f'<div class="resume-output">{st.session_state.resume_text}</div>', unsafe_allow_html=True)
            with cn:
                st.markdown("#### ✨ Improved")
                st.markdown(f'<div class="resume-output">{st.session_state.improved_resume}</div>', unsafe_allow_html=True)
            st.download_button("⬇️ Download as .txt", data=st.session_state.improved_resume,
                               file_name="improved_resume.txt", mime="text/plain", use_container_width=True)


# ── TAB 5: INTERVIEW PREP ─────────────────────────────────────────────────────
with tab5:
    if not ready:
        st.info("👈 Add your JD, resume, and API key in the sidebar to get started.")
    else:
        st.markdown("Generate likely interview questions with tailored suggested answers drawn from your resume.")

        if st.button("🎤 Generate Interview Questions", key="btn_interview"):
            with st.spinner("Preparing your interview guide…"):
                try:
                    from agent import run_interview_prep
                    st.session_state.interview_result = run_interview_prep(st.session_state.jd_text, st.session_state.resume_text)
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.interview_result:
            questions = st.session_state.interview_result.get("questions", [])

            if questions:
                # Category filter
                all_cats = sorted(set(q.get("category","Other") for q in questions))
                selected_cats = st.multiselect("Filter by category", all_cats, default=all_cats, key="cat_filter")
                filtered = [q for q in questions if q.get("category","Other") in selected_cats]

                st.markdown(f"**{len(filtered)} question{'s' if len(filtered)!=1 else ''}**")

                for i, q in enumerate(filtered, 1):
                    cat = q.get("category", "General")
                    color = CATEGORY_COLORS.get(cat, "#94a3b8")
                    with st.expander(f"Q{i} · {q.get('question','')[:80]}{'…' if len(q.get('question',''))>80 else ''}", expanded=i==1):
                        st.markdown(f"""
                        <div style="margin-bottom:8px;">
                          <span style="background:{color}22;color:{color};border:1px solid {color}44;
                                border-radius:20px;padding:3px 12px;font-size:11px;font-weight:700;
                                text-transform:uppercase;letter-spacing:1px;">{cat}</span>
                        </div>
                        <p style="font-size:16px;font-weight:600;color:var(--text);margin-bottom:10px;">{q.get('question','')}</p>
                        """, unsafe_allow_html=True)

                        why = q.get("why_asked","")
                        if why:
                            st.markdown(f'<div class="q-why">💡 <em>Why interviewers ask this:</em> {why}</div>', unsafe_allow_html=True)

                        st.markdown("**💬 Suggested Answer:**")
                        st.markdown(f'<div class="q-answer">{q.get("suggested_answer","")}</div>', unsafe_allow_html=True)


# ── TAB 6: COVER LETTER ───────────────────────────────────────────────────────
with tab6:
    if not ready:
        st.info("👈 Add your JD, resume, and API key in the sidebar to get started.")
    else:
        st.markdown("Generate a tailored cover letter that matches the tone and requirements of the JD.")
        st.caption("ℹ️ Only information from your resume is used — nothing is fabricated.")

        if st.button("✉️ Generate Cover Letter", key="btn_cover"):
            with st.spinner("Writing your cover letter…"):
                try:
                    from agent import run_cover_letter
                    st.session_state.cover_letter = run_cover_letter(st.session_state.jd_text, st.session_state.resume_text)
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.cover_letter:
            st.markdown("#### ✉️ Your Cover Letter")
            # Render with line breaks preserved
            rendered = st.session_state.cover_letter.replace("\n\n", "<br><br>").replace("\n", "<br>")
            st.markdown(f'<div class="cover-letter-output">{rendered}</div>', unsafe_allow_html=True)

            st.download_button("⬇️ Download as .txt", data=st.session_state.cover_letter,
                               file_name="cover_letter.txt", mime="text/plain", use_container_width=True)


# ── TAB 7: EXPORT ─────────────────────────────────────────────────────────────
with tab7:
    st.markdown("### 📥 Export Documents")
    st.markdown("Download any generated content as **PDF**, **DOCX**, or plain text.")

    if not (st.session_state.improved_resume or st.session_state.cover_letter or st.session_state.interview_result):
        st.info("Generate content in the other tabs first, then come back here to export.")
    else:
        from export_utils import (resume_to_docx, cover_letter_to_docx, interview_to_docx,
                                   resume_to_pdf, cover_letter_to_pdf)

        candidate_name = st.text_input("Your name (for the document header)", placeholder="e.g. Jane Smith", key="export_name")
        name = candidate_name.strip() if candidate_name.strip() else "Candidate"
        fname = name.replace(" ", "_")

        st.markdown("---")

        # ── Resume
        if st.session_state.improved_resume:
            st.markdown("#### ✨ Improved Resume")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.download_button("⬇️ PDF", key="dl_resume_pdf",
                    data=resume_to_pdf(st.session_state.improved_resume, name),
                    file_name=f"{fname}_resume.pdf", mime="application/pdf",
                    use_container_width=True)
            with c2:
                st.download_button("⬇️ DOCX", key="dl_resume_docx",
                    data=resume_to_docx(st.session_state.improved_resume, name),
                    file_name=f"{fname}_resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True)
            with c3:
                st.download_button("⬇️ TXT", key="dl_resume_txt",
                    data=st.session_state.improved_resume,
                    file_name=f"{fname}_resume.txt", mime="text/plain",
                    use_container_width=True)

        st.markdown("---")

        # ── Cover letter
        if st.session_state.cover_letter:
            st.markdown("#### ✉️ Cover Letter")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.download_button("⬇️ PDF", key="dl_cl_pdf",
                    data=cover_letter_to_pdf(st.session_state.cover_letter, name),
                    file_name=f"{fname}_cover_letter.pdf", mime="application/pdf",
                    use_container_width=True)
            with c2:
                st.download_button("⬇️ DOCX", key="dl_cl_docx",
                    data=cover_letter_to_docx(st.session_state.cover_letter, name),
                    file_name=f"{fname}_cover_letter.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True)
            with c3:
                st.download_button("⬇️ TXT", key="dl_cl_txt",
                    data=st.session_state.cover_letter,
                    file_name=f"{fname}_cover_letter.txt", mime="text/plain",
                    use_container_width=True)

        st.markdown("---")

        # ── Interview prep
        if st.session_state.interview_result:
            st.markdown("#### 🎤 Interview Prep Guide")
            questions = st.session_state.interview_result.get("questions", [])
            plain_iv = "\n\n".join(
                f"Q{i} [{q.get('category','')}]\n{q.get('question','')}\n\n"
                f"Why asked: {q.get('why_asked','')}\n\nSuggested Answer:\n{q.get('suggested_answer','')}"
                for i, q in enumerate(questions, 1)
            )
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("⬇️ DOCX", key="dl_iv_docx",
                    data=interview_to_docx(st.session_state.interview_result, name),
                    file_name=f"{fname}_interview_prep.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True)
            with c2:
                st.download_button("⬇️ TXT", key="dl_iv_txt",
                    data=plain_iv,
                    file_name=f"{fname}_interview_prep.txt", mime="text/plain",
                    use_container_width=True)