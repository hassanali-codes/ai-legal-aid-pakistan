"""
app.py - Main Streamlit application for the AI Legal Assistant.
Uses local CSV dataset (data/pakistan_laws.csv) - no Supabase required.
Run with: streamlit run app.py
"""

import os
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from backend.ingest import ingest_documents_from_csv
from backend.vector_store import build_vector_store, save_vector_store, load_vector_store
from backend.pipeline import run_rag_pipeline

# -- Load environment variables -----------------------------------------------
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# -- Page configuration -------------------------------------------------------
st.set_page_config(
    page_title="قانونی معاون | Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -- Session state ------------------------------------------------------------
if "chat_history"   not in st.session_state: st.session_state.chat_history   = []
if "vector_store"   not in st.session_state: st.session_state.vector_store   = None
if "docs_processed" not in st.session_state: st.session_state.docs_processed = False
if "dark_mode"      not in st.session_state: st.session_state.dark_mode      = True

def api_key_ok() -> bool:
    return bool(GROQ_API_KEY and GROQ_API_KEY.strip())

# -- Theme variables ----------------------------------------------------------
D = st.session_state.dark_mode

# Core palette
BG           = "#0b0f1a"        if D else "#f4f1ea"
SB_BG_START  = "#0d1525"        if D else "#fdfaf3"
SB_BG_END    = "#101828"        if D else "#f4f1ea"
SB_BORDER    = "rgba(212,175,55,0.18)" if D else "rgba(180,140,20,0.25)"
BODY_COLOR   = "#e2e8f0"        if D else "#1a1a2e"
SB_TEXT      = "#cbd5e1"        if D else "#2d3748"
SB_SUB       = "#64748b"        if D else "#6b7280"
SB_SEC_CLR   = "#475569"        if D else "#9ca3af"
DIVIDER_CLR  = "rgba(212,175,55,0.18)" if D else "rgba(180,140,20,0.22)"
HR_CLR       = "rgba(212,175,55,0.10)" if D else "rgba(180,140,20,0.18)"

HERO_BG      = "linear-gradient(135deg,#0d1a35 0%,#0b1422 40%,#0f1e38 100%)" if D else "linear-gradient(135deg,#fffdf5 0%,#fef9e7 40%,#fdf5e0 100%)"
HERO_BORDER  = "rgba(212,175,55,0.22)" if D else "rgba(180,140,20,0.30)"
HERO_TITLE   = "#d4af37"        if D else "#92710a"
HERO_SPAN    = "#e2e8f0"        if D else "#1a1a2e"
HERO_SUB     = "#64748b"        if D else "#6b7280"
HERO_URDU    = "#94a3b8"        if D else "#6b7280"

INPUT_BG     = "rgba(17,28,52,0.7)"   if D else "#ffffff"
INPUT_BD     = "rgba(212,175,55,0.2)" if D else "rgba(180,140,20,0.3)"
INPUT_CLR    = "#e2e8f0"        if D else "#1a1a2e"
INPUT_PH     = "#475569"        if D else "#9ca3af"
INPUT_FOCUS  = "rgba(212,175,55,0.5)" if D else "rgba(180,140,20,0.5)"
INPUT_GLOW   = "rgba(212,175,55,0.08)" if D else "rgba(180,140,20,0.10)"

BOT_BG       = "rgba(17,28,52,0.85)"  if D else "#ffffff"
BOT_BORDER   = "rgba(212,175,55,0.18)" if D else "rgba(180,140,20,0.28)"
BOT_TEXT     = "#cbd5e1"        if D else "#1a2634"
BOT_SHADOW   = "0 4px 16px rgba(0,0,0,0.3)" if D else "0 4px 16px rgba(0,0,0,0.08)"

EMPTY_TITLE  = "#475569"        if D else "#6b7280"
EMPTY_HINT   = "#334155"        if D else "#9ca3af"
DISCLAIMER   = "#334155"        if D else "#9ca3af"

LAW_TAG_BG   = "rgba(212,175,55,0.08)" if D else "rgba(180,140,20,0.07)"
LAW_TAG_BD   = "rgba(212,175,55,0.2)"  if D else "rgba(180,140,20,0.25)"
LAW_TAG_CLR  = "#d4af37"        if D else "#92710a"

BTN_TEXT     = "#0b0f1a"        if D else "#1a1a2e"

# -- Dynamic CSS --------------------------------------------------------------
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Inter:wght@300;400;500;600&family=Noto+Nastaliq+Urdu&display=swap');

  html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {BG};
    color: {BODY_COLOR};
  }}
  .stApp {{ background-color: {BG}; }}

  /* ─── Sidebar ─────────────────────────────────────── */
  [data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {SB_BG_START} 0%, {SB_BG_END} 100%);
    border-right: 1px solid {SB_BORDER};
  }}
  [data-testid="stSidebar"] * {{ color: {SB_TEXT} !important; }}

  .sb-logo {{ text-align:center; padding:1.4rem 0 0.8rem; }}
  .sb-logo .scales {{ font-size:3rem; line-height:1; }}
  .sb-logo .brand {{
    font-family:'Cinzel',serif; font-size:1.05rem; font-weight:700;
    letter-spacing:0.12em; color:#d4af37 !important; display:block; margin-top:0.4rem;
  }}
  .sb-logo .sub {{ font-size:0.72rem; color:{SB_SUB} !important; letter-spacing:0.08em; text-transform:uppercase; }}

  .sb-divider {{ border:none; border-top:1px solid {DIVIDER_CLR}; margin:0.9rem 0; }}
  .sb-section-title {{
    font-size:0.65rem; letter-spacing:0.15em; text-transform:uppercase;
    color:{SB_SEC_CLR} !important; font-weight:600; margin-bottom:0.6rem;
  }}

  /* ─── Pills ───────────────────────────────────────── */
  .pill {{
    display:inline-flex; align-items:center; gap:0.35rem;
    padding:0.3rem 0.85rem; border-radius:999px;
    font-size:0.78rem; font-weight:500; margin:0.15rem 0;
  }}
  .pill-green {{ background:rgba(16,185,129,0.12); color:#34d399 !important; border:1px solid rgba(52,211,153,0.25); }}
  .pill-red   {{ background:rgba(239,68,68,0.12);  color:#f87171 !important; border:1px solid rgba(248,113,113,0.25); }}

  /* ─── Law tags ────────────────────────────────────── */
  .law-tag {{
    display:inline-block; background:{LAW_TAG_BG}; border:1px solid {LAW_TAG_BD};
    color:{LAW_TAG_CLR} !important; border-radius:6px;
    padding:0.2rem 0.55rem; font-size:0.73rem; margin:0.15rem 0.1rem;
  }}

  /* ─── Theme toggle button ─────────────────────────── */
  .theme-toggle-btn > button {{
    background: transparent !important;
    border: 1px solid {SB_BORDER} !important;
    border-radius: 20px !important;
    color: {SB_TEXT} !important;
    font-size: 0.8rem !important;
    padding: 0.3rem 0.9rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
  }}
  .theme-toggle-btn > button:hover {{
    background: {LAW_TAG_BG} !important;
    border-color: {LAW_TAG_BD} !important;
  }}

  /* ─── Sidebar main buttons ────────────────────────── */
  .stButton > button {{
    background: linear-gradient(135deg,#b8952a 0%,#d4af37 50%,#b8952a 100%) !important;
    color: {BTN_TEXT} !important;
    border: none !important; border-radius:8px !important;
    font-weight:600 !important; font-size:0.85rem !important;
    letter-spacing:0.04em !important; padding:0.55rem 1.2rem !important;
    transition:all 0.2s ease !important; box-shadow:0 2px 12px rgba(212,175,55,0.25) !important;
  }}
  .stButton > button:hover {{
    box-shadow:0 4px 20px rgba(212,175,55,0.4) !important;
    transform:translateY(-1px) !important;
  }}
  [data-testid="stFormSubmitButton"] > button {{
    background: linear-gradient(135deg,#1e40af 0%,#3b82f6 100%) !important;
    color: white !important; border-radius:10px !important;
    font-weight:600 !important; padding:0.6rem 1.4rem !important;
    box-shadow:0 2px 12px rgba(59,130,246,0.3) !important; border:none !important;
  }}
  [data-testid="stFormSubmitButton"] > button:hover {{
    box-shadow:0 4px 20px rgba(59,130,246,0.5) !important;
    transform:translateY(-1px) !important;
  }}

  /* ─── Hero ────────────────────────────────────────── */
  .hero {{
    background: {HERO_BG};
    border: 1px solid {HERO_BORDER}; border-radius:16px;
    padding:2rem 2.5rem; margin-bottom:1.5rem;
    position:relative; overflow:hidden;
  }}
  .hero::before {{
    content:''; position:absolute; top:-60px; right:-60px;
    width:200px; height:200px;
    background:radial-gradient(circle,rgba(212,175,55,0.08) 0%,transparent 70%);
    pointer-events:none;
  }}
  .hero::after {{
    content:''; position:absolute; bottom:-40px; left:-40px;
    width:160px; height:160px;
    background:radial-gradient(circle,rgba(59,130,246,0.06) 0%,transparent 70%);
    pointer-events:none;
  }}
  .hero-title {{
    font-family:'Cinzel',serif; font-size:2rem; font-weight:700;
    color:{HERO_TITLE}; letter-spacing:0.06em; margin:0 0 0.3rem;
  }}
  .hero-title span {{ color:{HERO_SPAN}; }}
  .hero-sub   {{ font-size:0.93rem; color:{HERO_SUB}; margin:0; letter-spacing:0.02em; }}
  .hero-urdu  {{
    font-family:'Noto Nastaliq Urdu',serif; font-size:1rem;
    color:{HERO_URDU}; direction:rtl; margin-top:0.4rem;
  }}

  /* ─── Chat ────────────────────────────────────────── */
  .chat-wrap {{ display:flex; flex-direction:column; gap:1.1rem; padding:0.5rem 0 1rem; min-height:200px; }}
  .msg-row-user {{ display:flex; justify-content:flex-end; }}
  .msg-row-bot  {{ display:flex; justify-content:flex-start; align-items:flex-start; gap:0.7rem; }}

  .bubble-user {{
    background: linear-gradient(135deg,#1e3a6e 0%,#1e40af 100%);
    color:#e2e8f0; border-radius:18px 18px 4px 18px;
    padding:0.85rem 1.2rem; max-width:72%; font-size:0.95rem; line-height:1.65;
    box-shadow:0 4px 16px rgba(30,64,175,0.25); border:1px solid rgba(99,102,241,0.2);
  }}

  .bot-avatar {{
    width:36px; height:36px; min-width:36px;
    background:linear-gradient(135deg,#92710a 0%,#d4af37 100%);
    border-radius:50%; display:flex; align-items:center; justify-content:center;
    font-size:1rem; box-shadow:0 2px 8px rgba(212,175,55,0.3); margin-top:4px;
  }}
  .bubble-bot {{
    background:{BOT_BG}; border:1px solid {BOT_BORDER}; color:{BOT_TEXT};
    border-radius:4px 18px 18px 18px; padding:0.9rem 1.25rem; max-width:80%;
    font-size:0.95rem; line-height:1.8; box-shadow:{BOT_SHADOW};
    backdrop-filter:blur(8px);
    font-family:'Noto Nastaliq Urdu','Inter',sans-serif; direction:auto;
  }}
  .role-tag {{
    font-size:0.68rem; font-weight:600; letter-spacing:0.08em;
    text-transform:uppercase; margin-bottom:0.35rem; opacity:0.55;
  }}

  /* ─── Empty state ─────────────────────────────────── */
  .empty-state {{ text-align:center; padding:4rem 2rem; }}
  .empty-icon  {{ font-size:4rem; margin-bottom:1rem; filter:grayscale(30%); }}
  .empty-title {{ font-family:'Cinzel',serif; font-size:1.1rem; color:{EMPTY_TITLE}; margin-bottom:0.4rem; }}
  .empty-hint  {{ font-size:0.85rem; color:{EMPTY_HINT}; }}

  /* ─── Input ───────────────────────────────────────── */
  .stTextInput > div > div > input {{
    background:{INPUT_BG} !important; border:1px solid {INPUT_BD} !important;
    border-radius:12px !important; color:{INPUT_CLR} !important;
    padding:0.7rem 1.2rem !important; font-size:0.95rem !important;
    backdrop-filter:blur(8px); transition:border-color 0.2s,box-shadow 0.2s;
  }}
  .stTextInput > div > div > input::placeholder {{ color:{INPUT_PH} !important; }}
  .stTextInput > div > div > input:focus {{
    border-color:{INPUT_FOCUS} !important;
    box-shadow:0 0 0 3px {INPUT_GLOW} !important;
  }}

  /* ─── Misc ────────────────────────────────────────── */
  .stSpinner > div {{ border-color:#d4af37 transparent transparent !important; }}
  hr {{ border:none; border-top:1px solid {HR_CLR} !important; margin:1rem 0; }}
</style>
""", unsafe_allow_html=True)

# -- Sidebar ------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
      <div class="scales">⚖️</div>
      <span class="brand">LEGAL ASSISTANT</span>
      <span class="sub">Pakistan Law AI</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # ── Theme toggle ──────────────────────────────────────────────────────────
    st.markdown('<div class="sb-section-title">Appearance</div>', unsafe_allow_html=True)
    toggle_label = "☀️  Switch to Light Mode" if D else "🌙  Switch to Dark Mode"
    st.markdown('<div class="theme-toggle-btn">', unsafe_allow_html=True)
    if st.button(toggle_label, use_container_width=True, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # ── Status ────────────────────────────────────────────────────────────────
    st.markdown('<div class="sb-section-title">System Status</div>', unsafe_allow_html=True)
    if not api_key_ok():
        st.markdown('<span class="pill pill-red">🔑 API Key Missing</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="pill pill-green">✓ Groq API Ready</span>', unsafe_allow_html=True)

    if st.session_state.docs_processed:
        st.markdown('<span class="pill pill-green">✓ Knowledge Base Active</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="pill pill-red">✗ Knowledge Base Offline</span>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # ── Knowledge base ────────────────────────────────────────────────────────
    st.markdown('<div class="sb-section-title">Knowledge Base</div>', unsafe_allow_html=True)
    st.caption("Using local dataset: `data/pakistan_laws.csv`")

    init_btn = st.button("⚡ Initialize Knowledge Base", use_container_width=True)

    if init_btn:
        if not api_key_ok():
            st.error("Add GROQ_API_KEY to .env first.")
        else:
            with st.spinner("Building knowledge base…"):
                try:
                    chunks = ingest_documents_from_csv()
                    if not chunks:
                        st.error("No legal documents found in CSV.")
                    else:
                        vs = build_vector_store(chunks, GROQ_API_KEY)
                        save_vector_store(vs)
                        st.session_state.vector_store = vs
                        st.session_state.docs_processed = True
                        st.success(f"Ready — {len(chunks)} legal sections loaded.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Auto-load saved index
    if not st.session_state.docs_processed and api_key_ok():
        try:
            vs = load_vector_store(GROQ_API_KEY)
            st.session_state.vector_store = vs
            st.session_state.docs_processed = True
        except FileNotFoundError:
            pass
        except Exception as e:
            st.warning(f"Could not load index: {e}")

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # ── Covered laws ──────────────────────────────────────────────────────────
    st.markdown('<div class="sb-section-title">Covered Laws</div>', unsafe_allow_html=True)
    laws = [
        "Pakistan Penal Code", "Constitution", "CrPC",
        "Muslim Family Laws", "Rent Laws", "Labor Rights",
        "Islamic Banking", "Cyber Crime", "Consumer Rights", "Property Laws"
    ]
    tags_html = "".join(f'<span class="law-tag">{l}</span>' for l in laws)
    st.markdown(tags_html, unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="text-align:center;font-size:0.68rem;color:{DISCLAIMER};letter-spacing:0.06em;">'
        'FOR INFORMATIONAL PURPOSES ONLY<br>NOT A SUBSTITUTE FOR LEGAL COUNSEL'
        '</div>',
        unsafe_allow_html=True
    )


# -- Main area ----------------------------------------------------------------

# Floating theme toggle – fixed top-right beside the Deploy button
_fi  = "☀️" if D else "🌙"
_ft  = "Light Mode" if D else "Dark Mode"
_fc  = "#d4af37" if D else "#92710a"
_fbg = "rgba(13,26,53,0.88)" if D else "rgba(255,252,243,0.92)"
_fbd = "rgba(212,175,55,0.40)" if D else "rgba(180,140,20,0.35)"
_fsh = "0 2px 14px rgba(0,0,0,0.22)" if D else "0 2px 14px rgba(0,0,0,0.10)"
components.html(f"""
<script>
(function() {{
  var existing = window.parent.document.getElementById('_theme_float_btn');
  if (existing) existing.remove();
  var btn = window.parent.document.createElement('button');
  btn.id = '_theme_float_btn';
  btn.innerHTML = '{_fi}&nbsp;{_ft}';
  btn.title = '{_ft}';
  btn.style.cssText = 'position:fixed;top:10px;right:4.6rem;z-index:1000000;'
    + 'display:inline-flex;align-items:center;gap:6px;'
    + 'background:{_fbg};border:1px solid {_fbd};border-radius:20px;'
    + 'padding:5px 15px;cursor:pointer;font-size:0.82rem;font-weight:500;'
    + 'color:{_fc};font-family:Inter,sans-serif;letter-spacing:0.02em;'
    + 'backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);'
    + 'box-shadow:{_fsh};transition:all 0.2s ease;white-space:nowrap;';
  btn.onclick = function() {{
    var ps = window.parent.document.querySelectorAll('[data-testid=stSidebar] button p');
    for (var p of ps) {{
      if (p.textContent.includes('Mode')) {{ p.parentElement.click(); return; }}
    }}
  }};
  window.parent.document.body.appendChild(btn);
}})();
</script>
""", height=0)

api_icon = "✦" if api_key_ok() else "✗"
kb_icon  = "✦" if st.session_state.docs_processed else "✗"
api_cls  = "pill pill-green" if api_key_ok() else "pill pill-red"
kb_cls   = "pill pill-green" if st.session_state.docs_processed else "pill pill-red"
api_lbl  = "Groq API: Active" if api_key_ok() else "Groq API: Missing"
kb_lbl   = "Knowledge Base: Active" if st.session_state.docs_processed else "Knowledge Base: Offline"

st.markdown(f"""
<div class="hero">
  <div class="hero-title">⚖️ <span>AI</span> LEGAL ASSISTANT</div>
  <div class="hero-urdu">پاکستانی قوانین کے بارے میں سوال پوچھیں</div>
  <div class="hero-sub">Ask questions about Pakistan laws in Urdu or English</div>
  <div class="status-bar" style="margin-top:1rem;margin-bottom:0;">
    <span class="{api_cls}">{api_icon} {api_lbl}</span>
    <span class="{kb_cls}">{kb_icon} {kb_lbl}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Chat history
if st.session_state.chat_history:
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="msg-row-user">
              <div class="bubble-user">
                <div class="role-tag">You</div>
                {msg["content"]}
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            content_html = msg["content"].replace("\n", "<br>")
            st.markdown(f"""
            <div class="msg-row-bot">
              <div class="bot-avatar">⚖️</div>
              <div class="bubble-bot">
                <div class="role-tag">Legal Assistant</div>
                {content_html}
              </div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="empty-state">
      <div class="empty-icon">⚖️</div>
      <div class="empty-title">قانونی سوال پوچھیں</div>
      <div class="empty-hint">
        Initialize the knowledge base from the sidebar,<br>
        then type your question below.
      </div>
    </div>""", unsafe_allow_html=True)

# Chat input
st.markdown('<hr style="margin:0.5rem 0 1rem;">', unsafe_allow_html=True)
with st.form(key="chat_form", clear_on_submit=True):
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_query = st.text_input(
            label="Ask",
            placeholder="مثال: ضمانت کی شرائط کیا ہیں؟  /  What are the bail conditions?",
            label_visibility="collapsed",
        )
    with col_btn:
        submit = st.form_submit_button("Send ➤", use_container_width=True, type="primary")

if submit and user_query.strip():
    if not api_key_ok():
        st.error("Add your GROQ_API_KEY to the .env file.")
    elif not st.session_state.docs_processed or st.session_state.vector_store is None:
        st.warning("Please initialize the knowledge base from the sidebar first.")
    else:
        st.session_state.chat_history.append({"role": "user", "content": user_query.strip()})
        with st.spinner("Generating response…"):
            try:
                answer = run_rag_pipeline(
                    query=user_query.strip(),
                    vector_store=st.session_state.vector_store,
                    api_key=GROQ_API_KEY,
                )
            except Exception as e:
                answer = f"An error occurred: {e}"
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()
elif submit and not user_query.strip():
    st.warning("Please enter a question.")
