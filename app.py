"""
MockMentor AI — Company-Smart Mock Interview Coach
Main Streamlit Application
"""

import sys
import os
from pathlib import Path

# Ensure project root is in sys.path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import time

# ─── Page config (must be first Streamlit call) ───────────────────────────
st.set_page_config(
    page_title="MockMentor AI — Interview Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Imports ──────────────────────────────────────────────────────────────
from chains.memory import InterviewMemory
from agents.interviewer import fetch_interview_questions, conduct_interview_turn, get_opening_message
from agents.evaluator import evaluate_answer, get_score_label
from agents.coach import generate_coaching
from agents.report import compile_report, get_score_percentile
from utils.helpers import (
    create_radar_chart, create_score_timeline,
    create_score_gauge, format_score_badge, export_report_txt
)

# ─── Constants ────────────────────────────────────────────────────────────
COMPANIES = [
    "Google", "Amazon", "Microsoft", "TCS", "Infosys",
    "Wipro", "Accenture", "Goldman Sachs", "Deloitte", "Flipkart"
]

ROLES = [
    "Software Development Engineer",
    "Data Analyst",
    "Machine Learning Engineer",
    "Product Manager",
    "Business Analyst"
]

COMPANY_LOGOS = {
    "Google": "🔵", "Amazon": "🟠", "Microsoft": "🟩",
    "TCS": "🔷", "Infosys": "🟦", "Wipro": "🟤",
    "Accenture": "🟣", "Goldman Sachs": "🏦", "Deloitte": "⬛", "Flipkart": "🛒"
}

MODEL = "llama3.2"

# ─── Custom CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Global Reset ── */
* { font-family: 'Inter', sans-serif !important; }
html, body, [class*="css"] {
    background: #0a0f1e !important;
    color: #e2e8f0 !important;
}

/* ── App Container ── */
.stApp {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1529 50%, #0a1428 100%) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1529 0%, #111827 100%) !important;
    border-right: 1px solid rgba(99,102,241,0.2) !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* ── Main Content ── */
.main .block-container {
    padding: 1.5rem 2rem !important;
    max-width: 1200px !important;
}

/* ── Hero Header ── */
.hero-header {
    background: linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(168,85,247,0.1) 50%, rgba(236,72,153,0.08) 100%);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.2;
}
.hero-subtitle {
    color: #94a3b8;
    font-size: 1rem;
    margin-top: 0.4rem;
    font-weight: 400;
}

/* ── Cards ── */
.glass-card {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(10px);
    margin-bottom: 1rem;
    transition: border-color 0.3s ease, transform 0.2s ease;
}
.glass-card:hover {
    border-color: rgba(99,102,241,0.35);
    transform: translateY(-1px);
}

/* ── Chat Messages ── */
.chat-container {
    max-height: 500px;
    overflow-y: auto;
    padding: 1rem;
    scrollbar-width: thin;
    scrollbar-color: rgba(99,102,241,0.3) transparent;
}
.chat-message-ai {
    background: linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(99,102,241,0.06) 100%);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 16px 16px 16px 4px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    position: relative;
}
.chat-message-ai::before {
    content: '🤖';
    font-size: 1.1rem;
    display: block;
    margin-bottom: 0.4rem;
}
.chat-message-human {
    background: linear-gradient(135deg, rgba(168,85,247,0.12) 0%, rgba(236,72,153,0.06) 100%);
    border: 1px solid rgba(168,85,247,0.2);
    border-radius: 16px 16px 4px 16px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    text-align: right;
    position: relative;
}
.chat-message-human::after {
    content: '👤';
    font-size: 1.1rem;
    display: block;
    margin-top: 0.4rem;
}

/* ── Progress Bar ── */
.progress-container {
    background: rgba(15,23,42,0.6);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin-bottom: 1rem;
}
.progress-label {
    color: #94a3b8;
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 0.5rem;
}

/* ── Metric Cards ── */
.metric-card {
    background: rgba(15,23,42,0.7);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    transition: all 0.3s ease;
}
.metric-card:hover {
    border-color: rgba(99,102,241,0.4);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(99,102,241,0.15);
}
.metric-value {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6366f1, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.metric-label {
    color: #64748b;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
    margin-top: 0.3rem;
}

/* ── Company Badge ── */
.company-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.85rem;
    font-weight: 600;
    color: #a5b4fc;
}

/* ── Question Card ── */
.question-card {
    background: linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(15,23,42,0.8) 100%);
    border: 1px solid rgba(99,102,241,0.25);
    border-left: 4px solid #6366f1;
    border-radius: 0 12px 12px 0;
    padding: 1.2rem 1.5rem;
    margin: 0.8rem 0;
}
.question-number {
    color: #6366f1;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 700;
    margin-bottom: 0.4rem;
}
.question-text {
    color: #e2e8f0;
    font-size: 1.05rem;
    font-weight: 500;
    line-height: 1.6;
}

/* ── Difficulty Badge ── */
.difficulty-easy { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); border-radius: 8px; padding: 2px 10px; font-size: 0.75rem; font-weight: 600; }
.difficulty-medium { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); border-radius: 8px; padding: 2px 10px; font-size: 0.75rem; font-weight: 600; }
.difficulty-hard { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); border-radius: 8px; padding: 2px 10px; font-size: 0.75rem; font-weight: 600; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.5) !important;
}

/* ── Text inputs ── */
.stTextArea textarea {
    background: rgba(15,23,42,0.8) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-size: 0.95rem !important;
    transition: border-color 0.3s ease !important;
}
.stTextArea textarea:focus {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
}

/* ── Select boxes ── */
.stSelectbox > div > div {
    background: rgba(15,23,42,0.8) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* ── Divider ── */
hr { border-color: rgba(99,102,241,0.15) !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #6366f1 !important; }

/* ── Success/Warning/Error ── */
.stSuccess { background: rgba(16,185,129,0.1) !important; border: 1px solid rgba(16,185,129,0.3) !important; border-radius: 10px !important; }
.stWarning { background: rgba(245,158,11,0.1) !important; border: 1px solid rgba(245,158,11,0.3) !important; border-radius: 10px !important; }
.stError { background: rgba(239,68,68,0.1) !important; border: 1px solid rgba(239,68,68,0.3) !important; border-radius: 10px !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(15,23,42,0.6) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid rgba(99,102,241,0.15) !important;
}
.stTabs [data-baseweb="tab"] {
    color: #64748b !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(99,102,241,0.2) !important;
    color: #a5b4fc !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.3); border-radius: 3px; }

/* ── Evaluation result card ── */
.eval-card {
    background: rgba(15,23,42,0.6);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-top: 0.5rem;
}

/* ── Info box ── */
.info-box {
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 10px;
    padding: 0.8rem 1.1rem;
    color: #a5b4fc;
    font-size: 0.9rem;
}

/* ── Tag pills ── */
.tag-pill {
    display: inline-block;
    background: rgba(99,102,241,0.12);
    color: #818cf8;
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 20px;
    padding: 1px 10px;
    font-size: 0.75rem;
    margin: 2px;
}

/* ── Coaching sections ── */
.coaching-section {
    background: rgba(15,23,42,0.5);
    border: 1px solid rgba(168,85,247,0.2);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin: 0.8rem 0;
    line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)


# ─── Session State Initialisation ─────────────────────────────────────────
def init_session_state():
    defaults = {
        "memory": InterviewMemory(),
        "stage": "setup",          # setup → interview → results
        "chat_history": [],        # [{role, content}]
        "coaching_notes": "",
        "report_text": "",
        "vectorstore_ready": False,
        "current_answer_input": "",
        "is_processing": False,
        "evaluation_results": [],  # per-question evaluations for display
        "selected_company": None,
        "selected_role": None,
        "num_questions": 5,
        "difficulty_filter": "Mixed",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()

# ─── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem">
        <div style="font-size:2.5rem;margin-bottom:0.5rem">🎯</div>
        <div style="font-size:1.1rem;font-weight:700;background:linear-gradient(135deg,#6366f1,#a855f7);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">
            MockMentor AI
        </div>
        <div style="color:#64748b;font-size:0.75rem;margin-top:0.2rem">Company-Smart Interview Coach</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Vectorstore Setup
    st.markdown("**🗄️ Knowledge Base**")

    if not st.session_state.vectorstore_ready:
        st.markdown('<div class="info-box">Vector store not set up yet.<br>Click below to load question bank.</div>', unsafe_allow_html=True)
        if st.button("⚡ Setup Knowledge Base", use_container_width=True):
            with st.spinner("Building vector store (first time may take 2-3 minutes)..."):
                try:
                    from vectorstore.chroma_setup import setup_vectorstore
                    setup_vectorstore()
                    st.session_state.vectorstore_ready = True
                    st.success("✅ Knowledge base ready!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.markdown('<div class="info-box">✅ Knowledge base loaded<br>10 companies × 5 roles × 10 years</div>', unsafe_allow_html=True)

    st.divider()

    # Session Info
    if st.session_state.memory.session.get("company"):
        mem = st.session_state.memory.session
        cur, total = st.session_state.memory.progress
        st.markdown("**📊 Current Session**")
        st.markdown(f"""
        <div class="glass-card" style="padding:0.8rem">
            <div style="color:#6366f1;font-weight:700">{mem['company']}</div>
            <div style="color:#94a3b8;font-size:0.85rem">{mem['role']}</div>
            <div style="color:#64748b;font-size:0.8rem;margin-top:0.5rem">
                Question {cur}/{total}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Reset Button
    if st.button("🔄 New Interview", use_container_width=True):
        st.session_state.memory.reset()
        st.session_state.stage = "setup"
        st.session_state.chat_history = []
        st.session_state.coaching_notes = ""
        st.session_state.report_text = ""
        st.session_state.evaluation_results = []
        st.session_state.current_answer_input = ""
        st.rerun()

    st.divider()

    # App Info
    st.markdown("""
    <div style="color:#374151;font-size:0.72rem;text-align:center;line-height:1.6">
        <div style="color:#4b5563;font-weight:600;margin-bottom:0.3rem">Tech Stack</div>
        🦙 Ollama llama3.2<br>
        🔗 LangChain LCEL<br>
        🗄️ ChromaDB + RAG<br>
        📊 Plotly Charts<br>
        🎨 Streamlit
    </div>
    """, unsafe_allow_html=True)


# ─── Main Content ─────────────────────────────────────────────────────────

# Hero Header
st.markdown("""
<div class="hero-header">
    <h1 class="hero-title">🎯 MockMentor AI</h1>
    <p class="hero-subtitle">
        Company-smart mock interviews powered by a 10-year archive of real questions &amp; candidate feedback patterns.
        Realistic practice. Personalised coaching. Data-driven improvement.
    </p>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 1: SETUP
# ═══════════════════════════════════════════════════════════════════════════
if st.session_state.stage == "setup":

    st.markdown("### 🏢 Configure Your Mock Interview")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Target Company**")
        selected_company = st.selectbox(
            "Company",
            COMPANIES,
            format_func=lambda c: f"{COMPANY_LOGOS.get(c, '🏢')} {c}",
            label_visibility="collapsed",
            key="company_select"
        )

        st.markdown("**Number of Questions**")
        num_q = st.slider("Questions", 3, 8, 5, label_visibility="collapsed", key="num_q_slider")

    with col2:
        st.markdown("**Target Role**")
        selected_role = st.selectbox(
            "Role",
            ROLES,
            label_visibility="collapsed",
            key="role_select"
        )

        st.markdown("**Difficulty**")
        difficulty = st.select_slider(
            "Difficulty",
            options=["Easy Focus", "Mixed", "Hard Focus"],
            value="Mixed",
            label_visibility="collapsed",
            key="difficulty_slider"
        )

    # Company profile card
    st.markdown(f"""
    <div class="glass-card" style="margin-top:1rem">
        <div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.8rem">
            <span style="font-size:2rem">{COMPANY_LOGOS.get(selected_company, '🏢')}</span>
            <div>
                <div style="font-size:1.1rem;font-weight:700;color:#e2e8f0">{selected_company}</div>
                <div style="color:#6366f1;font-size:0.85rem;font-weight:500">{selected_role}</div>
            </div>
        </div>
        <div style="color:#64748b;font-size:0.85rem">
            📚 Retrieving from 10-year question archive &nbsp;|&nbsp;
            📊 {num_q} questions &nbsp;|&nbsp;
            ⚡ {difficulty} difficulty
        </div>
    </div>
    """, unsafe_allow_html=True)

    # What to expect
    st.markdown("""
    <div class="glass-card">
        <div style="font-weight:600;color:#a5b4fc;margin-bottom:0.8rem">🗺️ How the Interview Works</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.8rem">
            <div style="color:#94a3b8;font-size:0.85rem">
                <span style="color:#6366f1;font-weight:700">① Interviewer Agent</span><br>
                Asks company-specific questions retrieved from ChromaDB (RAG)
            </div>
            <div style="color:#94a3b8;font-size:0.85rem">
                <span style="color:#a855f7;font-weight:700">② Evaluator Agent</span><br>
                Scores your answers on correctness, depth &amp; communication
            </div>
            <div style="color:#94a3b8;font-size:0.85rem">
                <span style="color:#ec4899;font-weight:700">③ Coach Agent</span><br>
                Provides feedback grounded in historical candidate patterns
            </div>
            <div style="color:#94a3b8;font-size:0.85rem">
                <span style="color:#10b981;font-weight:700">④ Report Agent</span><br>
                Compiles your full session report with improvement plan
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Start button
    st.markdown("<br>", unsafe_allow_html=True)

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1.5, 1])
    with col_btn2:
        start_disabled = not st.session_state.vectorstore_ready
        if st.button(
            "🚀 Start Mock Interview" if not start_disabled else "⚡ Setup Knowledge Base First",
            use_container_width=True,
            disabled=start_disabled
        ):
            with st.spinner(f"🔍 Retrieving {selected_company} × {selected_role} questions from knowledge base..."):
                questions = fetch_interview_questions(
                    company=selected_company,
                    role=selected_role,
                    num_questions=num_q
                )

            if not questions:
                st.error(f"No questions found for {selected_company} + {selected_role}. Please try a different combination.")
            else:
                # Initialise session
                st.session_state.memory.start_session(selected_company, selected_role, questions)
                st.session_state.selected_company = selected_company
                st.session_state.selected_role = selected_role
                st.session_state.num_questions = num_q

                # Opening message
                opening = get_opening_message(selected_company, selected_role, questions[0])
                st.session_state.chat_history = [
                    {"role": "assistant", "content": opening}
                ]

                st.session_state.stage = "interview"
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 2: INTERVIEW
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "interview":

    mem = st.session_state.memory
    company = mem.session["company"]
    role = mem.session["role"]
    cur_q_idx, total_q = mem.progress
    current_q = mem.current_question

    # Progress bar
    progress_pct = cur_q_idx / total_q
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-label">
            <span style="color:#6366f1;font-weight:700">Question {cur_q_idx + 1 if current_q else cur_q_idx} of {total_q}</span>
            &nbsp;•&nbsp; <span class="company-badge">{COMPANY_LOGOS.get(company, '🏢')} {company} — {role}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(progress_pct)

    # Current question display
    if current_q:
        diff_class = f"difficulty-{current_q.get('difficulty', 'medium')}"
        tags_html = "".join(f'<span class="tag-pill">{t}</span>' for t in current_q.get("tags", "").split(", ")[:3])
        st.markdown(f"""
        <div class="question-card">
            <div class="question-number">Question {cur_q_idx + 1} · <span class="{diff_class}">{current_q.get('difficulty', 'medium').upper()}</span></div>
            <div class="question-text">{current_q['question']}</div>
            <div style="margin-top:0.6rem">{tags_html}</div>
        </div>
        """, unsafe_allow_html=True)

    # Chat history
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if msg["role"] == "assistant":
            st.markdown(f'<div class="chat-message-ai">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message-human">{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Latest evaluation result (after each answer)
    if st.session_state.evaluation_results:
        latest_eval = st.session_state.evaluation_results[-1]
        ev = latest_eval.get("evaluation", {})

        with st.expander("📊 Last Answer Evaluation", expanded=False):
            e1, e2, e3, e4 = st.columns(4)
            with e1:
                st.metric("Correctness", f"{ev.get('correctness', 0)}/10")
            with e2:
                st.metric("Depth", f"{ev.get('depth', 0)}/10")
            with e3:
                st.metric("Communication", f"{ev.get('communication', 0)}/10")
            with e4:
                st.metric("Overall", f"{ev.get('overall', 0):.1f}/10")

            if ev.get("covered_points"):
                st.markdown("**✅ What you covered:**")
                for p in ev.get("covered_points", []):
                    st.markdown(f"&nbsp;&nbsp;• {p}")

            if ev.get("missing_points"):
                st.markdown("**❌ What was missing:**")
                for p in ev.get("missing_points", []):
                    st.markdown(f"&nbsp;&nbsp;• {p}")

            if ev.get("quick_feedback"):
                st.info(ev["quick_feedback"])

    # Answer input
    if current_q and not mem.session.get("is_complete"):
        st.markdown("---")
        st.markdown("**✍️ Your Answer**")
        answer_text = st.text_area(
            "Type your answer here...",
            height=140,
            placeholder="Take your time. Think out loud. Use the STAR method for behavioral questions.",
            label_visibility="collapsed",
            key="answer_textarea"
        )

        col_submit, col_skip, col_hint = st.columns([2, 1, 2])

        with col_submit:
            if st.button("📤 Submit Answer", use_container_width=True):
                if not answer_text or len(answer_text.strip()) < 15:
                    st.warning("Please provide a more detailed answer (at least a few sentences).")
                else:
                    with st.spinner("🤖 Evaluating your answer..."):
                        # 1. Evaluate the answer
                        evaluation = evaluate_answer(
                            company=company,
                            role=role,
                            question=current_q["question"],
                            key_points=current_q.get("key_points", []),
                            answer=answer_text,
                            model=MODEL
                        )

                    with st.spinner("💬 Generating interviewer response..."):
                        # 2. Interviewer acknowledges and transitions
                        ai_response = conduct_interview_turn(
                            company=company,
                            role=role,
                            question=current_q,
                            user_input=answer_text,
                            history=mem.get_history(),
                            model=MODEL
                        )

                    # 3. Record the exchange
                    mem.save_exchange(answer_text, ai_response)
                    mem.record_answer(current_q["question"], answer_text, evaluation)

                    # 4. Update chat history
                    st.session_state.chat_history.append({"role": "user", "content": answer_text})
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

                    # 5. Store evaluation for display
                    st.session_state.evaluation_results.append({
                        "question": current_q["question"],
                        "answer": answer_text,
                        "evaluation": evaluation
                    })

                    # 6. Add next question to chat if interview continues
                    next_q = mem.current_question
                    if next_q and not mem.session.get("is_complete"):
                        next_q_msg = f"\n\n**Question {mem.session['current_q_index'] + 1}:** {next_q['question']}"
                        st.session_state.chat_history[-1]["content"] += next_q_msg

                    # 7. Check if interview is complete
                    if mem.session.get("is_complete"):
                        st.session_state.stage = "results"

                    st.rerun()

        with col_skip:
            if st.button("⏭️ Skip", use_container_width=True):
                # Record skip
                skip_eval = {
                    "correctness": 0, "depth": 0, "communication": 0, "overall": 0.0,
                    "covered_points": [], "missing_points": current_q.get("key_points", [])[:3],
                    "quick_feedback": "Question skipped."
                }
                mem.record_answer(current_q["question"], "[SKIPPED]", skip_eval)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": "*(Question skipped — moving on)*"}
                )
                if mem.session.get("is_complete"):
                    st.session_state.stage = "results"
                st.rerun()

        with col_hint:
            if st.button("💡 Show Hints", use_container_width=True):
                hints = current_q.get("key_points", [])[:3]
                st.info("**Key topics to touch on:** " + " • ".join(hints))

    elif mem.session.get("is_complete"):
        st.success("🎉 Interview complete! Generating your results...")
        time.sleep(1)
        st.session_state.stage = "results"
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 3: RESULTS
# ═══════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "results":

    mem = st.session_state.memory
    company = mem.session["company"]
    role = mem.session["role"]
    answers = mem.session["answers"]
    scores = mem.get_scores_summary()

    st.markdown(f"""
    <div style="text-align:center;padding:1.5rem 0">
        <div style="font-size:1.4rem;font-weight:800;color:#e2e8f0">Interview Complete! 🎉</div>
        <div style="color:#94a3b8;margin-top:0.3rem">
            {COMPANY_LOGOS.get(company, '🏢')} <strong>{company}</strong> — {role}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Score Overview
    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("Correctness", scores.get("avg_correctness", 0)),
        ("Depth", scores.get("avg_depth", 0)),
        ("Communication", scores.get("avg_communication", 0)),
        ("Overall", scores.get("avg_overall", 0)),
    ]

    for col, (label, val) in zip([col1, col2, col3, col4], metrics):
        with col:
            color = "#10b981" if val >= 7 else "#f59e0b" if val >= 4 else "#ef4444"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="background:linear-gradient(135deg,{color},{color}aa);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">
                    {val:.1f}
                </div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    # Percentile
    percentile = get_score_percentile(scores.get("avg_overall", 0), company)
    st.markdown(f"""
    <div style="text-align:center;margin:0.5rem 0 1rem">
        <div class="company-badge">📈 Estimated rank: {percentile} of {company} {role} candidates</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Tabs: Charts | Q&A Review | Coaching | Full Report
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Score Charts", "📝 Q&A Review", "🎯 AI Coaching", "📋 Full Report"
    ])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Performance Radar**")
            if scores:
                fig_radar = create_radar_chart(scores)
                st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

        with c2:
            st.markdown("**Score Progression**")
            if answers:
                fig_timeline = create_score_timeline(answers)
                st.plotly_chart(fig_timeline, use_container_width=True, config={"displayModeBar": False})

        # Overall gauge
        st.markdown("**Overall Performance Gauge**")
        fig_gauge = create_score_gauge(scores.get("avg_overall", 0), "Overall Interview Score")
        c3, c4, c5 = st.columns([1, 2, 1])
        with c4:
            st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

        # Strengths & Gaps
        col_s, col_g = st.columns(2)
        with col_s:
            st.markdown("**✅ Demonstrated Strengths**")
            for s in scores.get("top_strengths", [])[:5]:
                st.markdown(f"&nbsp;&nbsp;🟢 {s}")
            if not scores.get("top_strengths"):
                st.markdown("*No specific strengths detected*")

        with col_g:
            st.markdown("**❌ Key Gaps Identified**")
            for g in scores.get("top_gaps", [])[:5]:
                st.markdown(f"&nbsp;&nbsp;🔴 {g}")
            if not scores.get("top_gaps"):
                st.markdown("*No major gaps — great performance!*")

    with tab2:
        st.markdown("### 📝 Question-by-Question Review")
        for i, entry in enumerate(answers, 1):
            ev = entry.get("evaluation", {})
            overall = ev.get("overall", 0)
            color = "#10b981" if overall >= 7 else "#f59e0b" if overall >= 4 else "#ef4444"

            with st.expander(
                f"Q{i}: {entry['question'][:80]}{'...' if len(entry['question']) > 80 else ''} — {overall:.1f}/10",
                expanded=(i == 1)
            ):
                st.markdown(f"""
                <div style="border-left:3px solid {color};padding-left:1rem;margin-bottom:0.8rem">
                    <div style="color:#94a3b8;font-size:0.85rem;font-weight:600">QUESTION</div>
                    <div style="color:#e2e8f0">{entry['question']}</div>
                </div>
                """, unsafe_allow_html=True)

                if entry.get("answer") != "[SKIPPED]":
                    st.markdown(f"""
                    <div style="border-left:3px solid #a855f7;padding-left:1rem;margin-bottom:0.8rem">
                        <div style="color:#94a3b8;font-size:0.85rem;font-weight:600">YOUR ANSWER</div>
                        <div style="color:#e2e8f0">{entry.get('answer', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("⏭️ This question was skipped")

                e1, e2, e3, e4 = st.columns(4)
                with e1:
                    st.metric("Correctness", f"{ev.get('correctness', 0)}/10")
                with e2:
                    st.metric("Depth", f"{ev.get('depth', 0)}/10")
                with e3:
                    st.metric("Communication", f"{ev.get('communication', 0)}/10")
                with e4:
                    st.metric("Overall", f"{ev.get('overall', 0):.1f}/10")

                if ev.get("quick_feedback"):
                    st.info(f"💬 {ev['quick_feedback']}")

                col_cov, col_miss = st.columns(2)
                with col_cov:
                    if ev.get("covered_points"):
                        st.markdown("**✅ Covered:**")
                        for p in ev["covered_points"]:
                            st.markdown(f"• {p}")
                with col_miss:
                    if ev.get("missing_points"):
                        st.markdown("**❌ Missed:**")
                        for p in ev["missing_points"]:
                            st.markdown(f"• {p}")

    with tab3:
        st.markdown("### 🎯 AI-Powered Personalised Coaching")
        st.markdown(f"""
        <div class="info-box">
            🗄️ Coaching is grounded in historical feedback patterns retrieved from ChromaDB —
            real patterns from past {company} {role} candidates over 10 years.
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.coaching_notes:
            with st.spinner("🤖 Coach Agent analysing your performance against historical patterns..."):
                coaching = generate_coaching(
                    company=company,
                    role=role,
                    num_questions=len(answers),
                    avg_score=scores.get("avg_overall", 0),
                    main_gaps=scores.get("top_gaps", []),
                    strengths=scores.get("top_strengths", []),
                    model=MODEL
                )
                st.session_state.coaching_notes = coaching

        st.markdown(f"""
        <div class="coaching-section">
            {st.session_state.coaching_notes.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)

    with tab4:
        st.markdown("### 📋 Full Session Report")

        if not st.session_state.report_text:
            with st.spinner("📋 Report Agent compiling your session report..."):
                report = compile_report(
                    company=company,
                    role=role,
                    answers=answers,
                    scores_summary=scores,
                    coaching_notes=st.session_state.coaching_notes,
                    model=MODEL
                )
                st.session_state.report_text = report

        st.markdown(st.session_state.report_text)

        # Download button
        st.divider()
        col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
        with col_dl2:
            report_bytes = export_report_txt(
                st.session_state.report_text,
                company, role
            )
            st.download_button(
                label="⬇️ Download Report (.txt)",
                data=report_bytes,
                file_name=f"MockMentor_{company}_{role.replace(' ', '_')}_Report.txt",
                mime="text/plain",
                use_container_width=True
            )
