import streamlit as st
import pypdf
import json
import io
from google import genai

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StudyBuddy AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS  — Premium purple ed-tech aesthetic
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fraunces:ital,wght@0,300;0,700;0,900;1,300&display=swap');

/* ── CSS Variables ── */
:root {
  --purple-deep:   #3B0764;
  --purple-rich:   #6D28D9;
  --purple-mid:    #7C3AED;
  --purple-bright: #A855F7;
  --purple-soft:   #E9D5FF;
  --purple-tint:   #F5F0FF;
  --accent-gold:   #F59E0B;
  --accent-green:  #10B981;
  --accent-red:    #EF4444;
  --white:         #FFFFFF;
  --gray-50:       #F8F7FC;
  --gray-100:      #EDE9F6;
  --gray-400:      #A78BCA;
  --gray-600:      #6B5F8A;
  --gray-800:      #2D1F4A;
  --shadow-card:   0 4px 24px rgba(109,40,217,0.10);
  --shadow-hover:  0 8px 40px rgba(109,40,217,0.22);
  --radius-card:   18px;
  --radius-btn:    10px;
}

/* ── Global ── */
html, body, [class*="css"] {
  font-family: 'Plus Jakarta Sans', sans-serif;
  background-color: var(--gray-50) !important;
  color: var(--gray-800);
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--gray-100); }
::-webkit-scrollbar-thumb { background: var(--purple-soft); border-radius: 4px; }

/* ── Main background ── */
[data-testid="stAppViewContainer"] {
  background: linear-gradient(160deg, #F5F0FF 0%, #FAF8FF 50%, #F0EBFF 100%) !important;
}
[data-testid="stHeader"] { background: transparent !important; }

/* ── Streamlit Native UI Styling (Menu Buttons & Sidebar Arrow) ── */
/* Changes the color of the 3-dots menu icons to deep purple */
button[data-testid="baseButton-headerNoPadding"] svg {
  fill: var(--purple-rich) !important;
  color: var(--purple-rich) !important;
}

/* Changes the sidebar collapse/expand arrow toggle color to deep purple */
button[data-testid="stSidebarCollapseButton"] svg {
  fill: var(--purple-rich) !important;
  color: var(--purple-rich) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, var(--purple-deep) 0%, #1E0A4A 100%) !important;
  border-right: none !important;
  box-shadow: 4px 0 30px rgba(59,7,100,0.3);
}
[data-testid="stSidebar"] * { color: #E9D5FF !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #FFFFFF !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { font-size: 0.88rem; line-height: 1.6; }

/* sidebar radio pill style */
[data-testid="stSidebar"] .stRadio > div {
  background: rgba(255,255,255,0.07);
  border-radius: 12px;
  padding: 0.5rem 0.75rem;
  border: 1px solid rgba(168,85,247,0.3);
}

/* ── Headings ── */
h1, h2, h3 { font-family: 'Fraunces', serif !important; }

/* ── Hero ── */
.hero-wrap {
  background: linear-gradient(135deg, var(--purple-deep) 0%, var(--purple-mid) 60%, #9333EA 100%);
  border-radius: 24px;
  padding: 2.8rem 3rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 16px 60px rgba(109,40,217,0.35);
}
.hero-wrap::before {
  content: '';
  position: absolute;
  top: -60px; right: -60px;
  width: 280px; height: 280px;
  background: radial-gradient(circle, rgba(168,85,247,0.35) 0%, transparent 70%);
  border-radius: 50%;
}
.hero-wrap::after {
  content: '';
  position: absolute;
  bottom: -80px; left: 30%;
  width: 200px; height: 200px;
  background: radial-gradient(circle, rgba(245,158,11,0.15) 0%, transparent 65%);
  border-radius: 50%;
}
.hero-title {
  font-family: 'Fraunces', serif;
  font-size: 2.8rem;
  font-weight: 900;
  color: #FFFFFF;
  line-height: 1.15;
  margin: 0 0 0.5rem;
  position: relative;
  z-index: 1;
}
.hero-title span { color: var(--accent-gold); font-style: italic; }
.hero-sub {
  font-size: 1.05rem;
  color: #DDD6FE;
  font-weight: 300;
  position: relative;
  z-index: 1;
  max-width: 520px;
}
.hero-badge {
  display: inline-block;
  background: rgba(245,158,11,0.2);
  border: 1px solid rgba(245,158,11,0.5);
  color: var(--accent-gold);
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  padding: 0.3rem 0.75rem;
  border-radius: 20px;
  margin-bottom: 1rem;
  position: relative;
  z-index: 1;
}

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
  background: var(--white) !important;
  border: 2px dashed var(--purple-soft) !important;
  border-radius: var(--radius-card) !important;
  padding: 1.2rem !important;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--purple-bright) !important;
  box-shadow: var(--shadow-card) !important;
}

/* ── Buttons ── */
.stButton > button {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-weight: 700 !important;
  font-size: 0.88rem !important;
  letter-spacing: 0.03em !important;
  border-radius: var(--radius-btn) !important;
  transition: all 0.22s cubic-bezier(.4,0,.2,1) !important;
  border: none !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, var(--purple-rich) 0%, var(--purple-bright) 100%) !important;
  color: white !important;
  box-shadow: 0 4px 15px rgba(109,40,217,0.4) !important;
}
.stButton > button[kind="primary"]:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(109,40,217,0.55) !important;
}
.stButton > button[kind="secondary"] {
  background: var(--white) !important;
  color: var(--purple-rich) !important;
  border: 2px solid var(--purple-soft) !important;
}
.stButton > button[kind="secondary"]:hover {
  border-color: var(--purple-bright) !important;
  background: var(--purple-tint) !important;
  transform: translateY(-1px) !important;
}

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div > div {
  background: linear-gradient(90deg, var(--purple-rich), var(--purple-bright)) !important;
  border-radius: 10px !important;
}

/* ── Card blocks (HTML) ── */
.card {
  background: var(--white);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
  padding: 2rem;
  margin-bottom: 1.2rem;
  border: 1px solid var(--gray-100);
  transition: box-shadow 0.25s ease;
  animation: fadeUp 0.4s ease both;
}
.card:hover { box-shadow: var(--shadow-hover); }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── Flashcard ── */
.flashcard {
  background: linear-gradient(145deg, var(--purple-deep) 0%, #4C1D95 100%);
  border-radius: 22px;
  padding: 3rem 2.5rem;
  text-align: center;
  min-height: 240px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 12px 48px rgba(59,7,100,0.35);
  position: relative;
  overflow: hidden;
}
.flashcard::before {
  content: '';
  position: absolute;
  top: -40px; right: -40px;
  width: 180px; height: 180px;
  background: radial-gradient(circle, rgba(168,85,247,0.3) 0%, transparent 70%);
  border-radius: 50%;
}
.fc-chip {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--accent-gold);
  background: rgba(245,158,11,0.15);
  border: 1px solid rgba(245,158,11,0.35);
  padding: 0.28rem 0.8rem;
  border-radius: 20px;
  margin-bottom: 1.4rem;
  position: relative;
  z-index: 1;
}
.fc-question {
  font-family: 'Fraunces', serif;
  font-size: 1.35rem;
  font-weight: 700;
  color: #FFFFFF;
  line-height: 1.55;
  position: relative;
  z-index: 1;
}
.fc-answer {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(168,85,247,0.4);
  border-radius: 14px;
  padding: 1.1rem 1.4rem;
  margin-top: 1.5rem;
  font-size: 0.97rem;
  color: #E9D5FF;
  text-align: left;
  line-height: 1.7;
  width: 100%;
  position: relative;
  z-index: 1;
}
.fc-counter {
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: var(--gray-400);
  text-align: center;
  margin-top: 0.8rem;
}

/* ── MCQ Card ── */
.mcq-card {
  background: var(--white);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
  padding: 2.2rem 2.4rem;
  border-left: 5px solid var(--purple-rich);
  margin-bottom: 1.2rem;
  animation: fadeUp 0.35s ease both;
}
.mcq-question {
  font-family: 'Fraunces', serif;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--gray-800);
  line-height: 1.55;
  margin-bottom: 1.4rem;
}
.mcq-chip {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--purple-bright);
  background: var(--purple-tint);
  border: 1px solid var(--purple-soft);
  padding: 0.28rem 0.75rem;
  border-radius: 20px;
  display: inline-block;
  margin-bottom: 0.9rem;
}

/* ── Feedback boxes ── */
.feedback-correct {
  background: #ECFDF5;
  border: 1.5px solid #6EE7B7;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  color: #065F46;
  font-weight: 600;
  margin-top: 0.8rem;
  animation: fadeUp 0.3s ease both;
}
.feedback-wrong {
  background: #FEF2F2;
  border: 1.5px solid #FCA5A5;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  color: #991B1B;
  font-weight: 600;
  margin-top: 0.8rem;
  animation: fadeUp 0.3s ease both;
}
.explanation-box {
  background: var(--purple-tint);
  border: 1px solid var(--purple-soft);
  border-radius: 12px;
  padding: 0.9rem 1.1rem;
  color: var(--purple-deep);
  font-size: 0.92rem;
  margin-top: 0.6rem;
  line-height: 1.65;
  animation: fadeUp 0.4s ease 0.1s both;
}

/* ── Score banner ── */
.score-banner {
  background: linear-gradient(135deg, var(--purple-deep), var(--purple-mid));
  border-radius: 18px;
  padding: 1.6rem 2rem;
  display: flex;
  align-items: center;
  gap: 1.2rem;
  box-shadow: 0 8px 30px rgba(109,40,217,0.3);
  margin-bottom: 1.5rem;
}
.score-number {
  font-family: 'Fraunces', serif;
  font-size: 3rem;
  font-weight: 900;
  color: var(--accent-gold);
  line-height: 1;
}
.score-label {
  font-size: 0.9rem;
  color: #DDD6FE;
}
.score-title {
  font-family: 'Fraunces', serif;
  font-size: 1.15rem;
  font-weight: 700;
  color: white;
}

/* ── Section header ── */
.section-header {
  font-family: 'Fraunces', serif;
  font-size: 1.45rem;
  font-weight: 700;
  color: var(--purple-deep);
  margin-bottom: 0.2rem;
}
.section-sub {
  font-size: 0.88rem;
  color: var(--gray-600);
  margin-bottom: 1.4rem;
}
.divider {
  border: none;
  border-top: 1.5px solid var(--gray-100);
  margin: 1.8rem 0;
}

/* ── Empty state ── */
.empty-state {
  background: var(--white);
  border: 2px dashed var(--purple-soft);
  border-radius: 22px;
  padding: 4rem 2rem;
  text-align: center;
}
.empty-icon { font-size: 3.2rem; margin-bottom: 0.8rem; }
.empty-title { font-family: 'Fraunces', serif; font-size: 1.3rem; font-weight: 700; color: var(--gray-800); }
.empty-text  { font-size: 0.9rem; color: var(--gray-600); margin-top: 0.4rem; }

/* ── Sidebar tip ── */
.sb-tip {
  background: rgba(168,85,247,0.12);
  border: 1px solid rgba(168,85,247,0.25);
  border-radius: 10px;
  padding: 0.8rem 1rem;
  font-size: 0.82rem;
  color: #C4B5FD !important;
  line-height: 1.6;
  margin-top: 0.5rem;
}
.sb-divider {
  border: none;
  border-top: 1px solid rgba(168,85,247,0.2);
  margin: 1.2rem 0;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: var(--purple-bright) !important; }

/* ── Radio options text color high contrast fix ── */
div[data-testid="stAppViewContainer"] .stRadio label p {
  color: var(--gray-800) !important;
  font-weight: 600 !important;
}

/* ── Sidebar study format header and radio selection pure white fix ── */
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] div[role="radiogroup"] label *,
[data-testid="stSidebar"] .stRadio div p,
[data-testid="stSidebar"] .stRadio label span {
  color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# GEMINI CLIENT  (cached — initialised once)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_gemini_client():
    try:
        return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception:
        st.error(
            "⚠️ **API key missing.** "
            "Add `GEMINI_API_KEY = '...'` to `.streamlit/secrets.toml` and restart."
        )
        st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def extract_pdf_text(uploaded_file) -> str:
    """Extract all text from an uploaded PDF via pypdf."""
    reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
    pages = [p.extract_text() for p in reader.pages if p.extract_text()]
    return "\n\n".join(pages)


def _clean_json(raw: str) -> str:
    """Strip accidental markdown fences from Gemini response."""
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) >= 2 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    if raw.endswith("```"):
        raw = raw[:-3]
    return raw.strip()


def generate_flashcards(client, text: str, n: int) -> list[dict]:
    prompt = f"""You are an expert study-card generator.
Read the study material below and create exactly {n} high-quality flashcards.

STRICT OUTPUT RULES — follow exactly:
1. Return ONLY a raw JSON array. No markdown, no code fences, no commentary.
2. Each element must be a JSON object with exactly two keys: "question" and "answer".
3. Questions should test conceptual understanding, not trivial recall.
4. Answers: 1-3 concise, complete sentences.

Required format (no deviations):
[{{"question": "...", "answer": "..."}}, ...]

--- STUDY MATERIAL (first ~12000 chars) ---
{text[:12000]}
"""
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    cards = json.loads(_clean_json(response.text))
    validated = [
        {"question": str(c["question"]), "answer": str(c["answer"])}
        for c in cards if isinstance(c, dict) and "question" in c and "answer" in c
    ]
    if not validated:
        raise ValueError("No valid flashcards found in Gemini response.")
    return validated


def generate_mcqs(client, text: str, n: int) -> list[dict]:
    prompt = f"""You are an expert quiz designer.
Read the study material below and create exactly {n} multiple-choice questions.

STRICT OUTPUT RULES — follow exactly:
1. Return ONLY a raw JSON array. No markdown, no code fences, no commentary.
2. Each element must be a JSON object with exactly four keys:
   - "question": the question string
   - "options": a JSON array of exactly 4 strings (the answer choices)
   - "correct_answer": the EXACT string from "options" that is correct
   - "explanation": 1-2 sentences explaining why the correct answer is right
3. Options should be plausible distractors — not obviously wrong.
4. Do NOT label options with A/B/C/D inside the strings; labels are added by the UI.

Required format:
[{{"question":"...","options":["...","...","...","..."],"correct_answer":"...","explanation":"..."}}]

--- STUDY MATERIAL (first ~12000 chars) ---
{text[:12000]}
"""
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    questions = json.loads(_clean_json(response.text))
    validated = []
    for q in questions:
        if (
            isinstance(q, dict)
            and "question" in q
            and "options" in q
            and "correct_answer" in q
            and "explanation" in q
            and isinstance(q["options"], list)
            and len(q["options"]) == 4
            and q["correct_answer"] in q["options"]
        ):
            validated.append({
                "question":       str(q["question"]),
                "options":        [str(o) for o in q["options"]],
                "correct_answer": str(q["correct_answer"]),
                "explanation":    str(q["explanation"]),
            })
    if not validated:
        raise ValueError("No valid MCQs found in Gemini response.")
    return validated


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE  — initialise all keys once
# ─────────────────────────────────────────────────────────────────────────────
defaults = {
    "flashcards":      [],
    "mcqs":            [],
    "fc_index":        0,
    "fc_show_answer":  False,
    "mcq_index":       0,
    "mcq_answers":     {},   # {index: chosen_option_string}
    "mcq_checked":     {},   # {index: True/False}
    "score":           0,
    "mode":            "Flashcards",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 StudyBuddy AI")
    st.markdown("*Your AI-powered learning companion*")
    st.markdown("<hr class='sb-divider'>", unsafe_allow_html=True)

    # ── Study Mode Selector ──
    st.markdown("### 🗂 Select Study Format")
    study_mode = st.radio(
        label="study_mode_radio",
        options=["Flashcards", "Multiple Choice (MCQ)"],
        index=0 if st.session_state.mode == "Flashcards" else 1,
        label_visibility="collapsed",
    )
    st.session_state.mode = study_mode

    st.markdown("<hr class='sb-divider'>", unsafe_allow_html=True)

    # ── Settings ──
    st.markdown("### ⚙️ Settings")
    num_items = st.slider(
        "Number of questions / cards",
        min_value=3, max_value=20, value=8, step=1,
    )

    st.markdown("<hr class='sb-divider'>", unsafe_allow_html=True)

    # ── How to use ──
    st.markdown("### 📋 How to Use")
    if study_mode == "Flashcards":
        st.markdown(
            "1. Upload a **PDF** (notes, slides, article).\n"
            "2. Click **Generate Flashcards**.\n"
            "3. Use ◀ ▶ to navigate cards.\n"
            "4. Click **Reveal Answer** to check yourself."
        )
    else:
        st.markdown(
            "1. Upload a **PDF** study material.\n"
            "2. Click **Generate MCQs**.\n"
            "3. Pick an answer for each question.\n"
            "4. Click **Check Answer** for instant feedback."
        )

    st.markdown(
        '<div class="sb-tip">💡 Best results with focused PDFs of 5–20 pages. '
        'Very large documents are trimmed to ~12 000 characters.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Powered by Gemini 2.5 Flash · Built with Streamlit")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN AREA
# ─────────────────────────────────────────────────────────────────────────────

# ── Hero Banner ──
mode_icon = "🃏" if study_mode == "Flashcards" else "🧩"
st.markdown(f"""
<div class="hero-wrap">
  <div class="hero-badge">{mode_icon} {study_mode} Mode Active</div>
  <div class="hero-title">Study<span>Buddy</span> AI</div>
  <div class="hero-sub">
    Upload your notes, let Flash ai transform them into 
    interactive {'flashcards' if study_mode == 'Flashcards' else 'multiple-choice quizzes'} 
    — and learn smarter.
  </div>
</div>
""", unsafe_allow_html=True)

# ── Upload + Generate ──
col_upload, col_info = st.columns([3, 2], gap="large")

with col_upload:
    st.markdown('<div class="section-header">📄 Upload Study Material</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Drag and drop a PDF below</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drop PDF here",
        type=["pdf"],
        label_visibility="collapsed",
    )

with col_info:
    st.markdown('<div class="section-header">🚀 Generate</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-sub">Click below to create {num_items} '
        f'{"flashcards" if study_mode == "Flashcards" else "MCQs"} from your PDF.</div>',
        unsafe_allow_html=True,
    )
    generate_btn = st.button(
        f"✨ Generate {'Flashcards' if study_mode == 'Flashcards' else 'MCQs'}",
        type="primary",
        use_container_width=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# GENERATION LOGIC
# ─────────────────────────────────────────────────────────────────────────────
if generate_btn:
    if uploaded_file is None:
        st.warning("⚠️ Please upload a PDF first.")
    else:
        label = "flashcards" if study_mode == "Flashcards" else "MCQs"
        with st.spinner(f"Reading your PDF and crafting {num_items} {label} with Gemini 2.5 Flash…"):
            raw_text = extract_pdf_text(uploaded_file)

            if not raw_text.strip():
                st.error(
                    "❌ Could not extract text from this PDF. "
                    "It may be a scanned/image-only document. Please use a text-based PDF."
                )
                st.stop()

            client = get_gemini_client()
            try:
                if study_mode == "Flashcards":
                    cards = generate_flashcards(client, raw_text, num_items)
                    st.session_state.flashcards     = cards
                    st.session_state.fc_index       = 0
                    st.session_state.fc_show_answer = False
                    st.success(f"🎉 {len(cards)} flashcards ready! Scroll down to start.")
                else:
                    mcqs = generate_mcqs(client, raw_text, num_items)
                    st.session_state.mcqs        = mcqs
                    st.session_state.mcq_index   = 0
                    st.session_state.mcq_answers = {}
                    st.session_state.mcq_checked = {}
                    st.session_state.score       = 0
                    st.success(f"🎉 {len(mcqs)} MCQs ready! Test yourself below.")

            except json.JSONDecodeError:
                st.error("Gemini returned an unexpected format. Please try again — this is usually transient.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")


st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ── FLASHCARD QUIZ UI ────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
if study_mode == "Flashcards":

    cards = st.session_state.flashcards

    if not cards:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">🃏</div>
          <div class="empty-title">No flashcards yet</div>
          <div class="empty-text">Upload a PDF and click <b>Generate Flashcards</b> to get started.</div>
        </div>""", unsafe_allow_html=True)

    else:
        idx   = st.session_state.fc_index
        total = len(cards)
        card  = cards[idx]

        st.markdown(f'<div class="section-header">📚 Flashcard Quiz</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="section-sub">Card {idx + 1} of {total} — '
            f'use the buttons below to navigate.</div>',
            unsafe_allow_html=True,
        )

        # Progress bar
        st.progress((idx + 1) / total, text=f"Progress: {idx + 1} / {total}")
        st.markdown("<br>", unsafe_allow_html=True)

        # Flashcard
        answer_html = ""
        if st.session_state.fc_show_answer:
            answer_html = f'<div class="fc-answer">💡 {card["answer"]}</div>'

        st.markdown(f"""
        <div class="flashcard">
          <div class="fc-chip">Question {idx + 1} of {total}</div>
          <div class="fc-question">{card["question"]}</div>
          {answer_html}
        </div>
        <div class="fc-counter">Card {idx + 1} / {total}</div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Navigation controls
        c1, c2, c3, c4, c5 = st.columns([1.1, 1.1, 1.8, 1.1, 1.1])

        with c1:
            if st.button("◀ Prev", use_container_width=True, disabled=(idx == 0), type="secondary"):
                st.session_state.fc_index       -= 1
                st.session_state.fc_show_answer  = False
                st.rerun()

        with c2:
            if st.button("Next ▶", use_container_width=True, disabled=(idx == total - 1), type="secondary"):
                st.session_state.fc_index       += 1
                st.session_state.fc_show_answer  = False
                st.rerun()

        with c3:
            if not st.session_state.fc_show_answer:
                if st.button("🔍 Reveal Answer", use_container_width=True, type="primary"):
                    st.session_state.fc_show_answer = True
                    st.rerun()
            else:
                if st.button("🙈 Hide Answer", use_container_width=True, type="primary"):
                    st.session_state.fc_show_answer = False
                    st.rerun()

        with c5:
            if st.button("🔄 Reset", use_container_width=True, type="secondary"):
                st.session_state.fc_index       = 0
                st.session_state.fc_show_answer = False
                st.rerun()

        # Expandable full list
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📋 View all flashcards"):
            for i, c in enumerate(cards, 1):
                st.markdown(f"**Q{i}:** {c['question']}")
                st.markdown(f"*A:* {c['answer']}")
                if i < total:
                    st.markdown("---")


# ─────────────────────────────────────────────────────────────────────────────
# ── MCQ QUIZ UI ──────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
else:
    mcqs = st.session_state.mcqs

    if not mcqs:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">🧩</div>
          <div class="empty-title">No questions yet</div>
          <div class="empty-text">Upload a PDF and click <b>Generate MCQs</b> to start your quiz.</div>
        </div>""", unsafe_allow_html=True)

    else:
        total   = len(mcqs)
        answers = st.session_state.mcq_answers
        checked = st.session_state.mcq_checked

        # ── Score Banner ──
        answered_count = len(checked)
        correct_count  = sum(1 for i, ans in answers.items() if checked.get(i) and ans == mcqs[i]["correct_answer"])

        if answered_count > 0:
            st.markdown(f"""
            <div class="score-banner">
              <div>
                <div class="score-number">{correct_count}/{answered_count}</div>
              </div>
              <div>
                <div class="score-title">Your Score</div>
                <div class="score-label">{total - answered_count} questions remaining</div>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f'<div class="section-header">🧩 MCQ Quiz</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="section-sub">{total} questions generated — select an answer and click Check.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        # ── Render each question ──
        LABELS = ["A", "B", "C", "D"]

        for i, q in enumerate(mcqs):
            is_checked = checked.get(i, False)
            user_ans   = answers.get(i, None)
            is_correct = (user_ans == q["correct_answer"])

            # Build labeled options for display
            labeled_options = [f"{LABELS[j]}.  {opt}" for j, opt in enumerate(q["options"])]
            correct_labeled = next(
                f"{LABELS[j]}.  {opt}"
                for j, opt in enumerate(q["options"])
                if opt == q["correct_answer"]
            )

            # Rebuild the answer key to map labeled → raw
            label_to_raw = {f"{LABELS[j]}.  {opt}": opt for j, opt in enumerate(q["options"])}

            border_color = (
                "#10B981" if (is_checked and is_correct)
                else "#EF4444" if (is_checked and not is_correct)
                else "#6D28D9"
            )

            st.markdown(f"""
            <div class="mcq-card" style="border-left-color:{border_color};">
              <div class="mcq-chip">Question {i + 1} of {total}</div>
              <div class="mcq-question">{q["question"]}</div>
            </div>""", unsafe_allow_html=True)

            # Radio — disable after checking
            chosen_labeled = st.radio(
                label=f"q_{i}",
                options=labeled_options,
                index=labeled_options.index(
                    next((f"{LABELS[j]}.  {opt}" for j, opt in enumerate(q["options"]) if opt == user_ans), labeled_options[0])
                ) if user_ans else None,
                label_visibility="collapsed",
                key=f"radio_{i}",
                disabled=is_checked,
            )

            # Map back to raw answer
            if chosen_labeled:
                st.session_state.mcq_answers[i] = label_to_raw.get(chosen_labeled, chosen_labeled)

            # Check Answer button
            btn_col, _ = st.columns([1, 3])
            with btn_col:
                if not is_checked:
                    if st.button("✔ Check Answer", key=f"check_{i}", type="primary", use_container_width=True):
                        if i in st.session_state.mcq_answers:
                            st.session_state.mcq_checked[i] = True
                            st.rerun()
                        else:
                            st.warning("Please select an option first.")

            # Feedback
            if is_checked:
                if is_correct:
                    st.markdown(
                        f'<div class="feedback-correct">✅ Correct! Well done.</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="feedback-wrong">'
                        f'❌ Incorrect. The correct answer is: <b>{correct_labeled}</b>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown(
                    f'<div class="explanation-box">📖 <b>Explanation:</b> {q["explanation"]}</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)

        # ── Completion Banner ──
        if len(checked) == total:
            pct = round(correct_count / total * 100)
            grade = "🏆 Excellent!" if pct >= 80 else "👍 Good effort!" if pct >= 50 else "📖 Keep studying!"
            st.balloons()
            st.success(
                f"{grade}  You scored **{correct_count} / {total}** ({pct}%). "
                "Click **Generate MCQs** again to retry with fresh questions."
            )
