import re
import textwrap
import time

import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types

from email_service import send_email_digest
from prompts import SUMMARY_REQUEST_PROMPT, SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE


st.set_page_config(
    page_title="MacroSnap | AI nutrition intelligence",
    page_icon="🍋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DEFAULT_MODEL = "gemini-3.8-flash"
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
MODEL_NAME = st.secrets.get("GEMINI_MODEL", DEFAULT_MODEL)
GMAIL_ADDRESS = st.secrets.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = st.secrets.get("GMAIL_APP_PASSWORD", "")
MACROSNAP_URL = st.secrets.get("MACROSNAP_URL", "")


def render_html(html: str) -> None:
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)


def init_state() -> None:
    defaults = {
        "onboarded": False,
        "messages": [],
        "chat": None,
        "name": "",
        "email": "",
        "active_model": MODEL_NAME,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


@st.cache_resource
def get_gemini_client(api_key: str):
    if not api_key:
        return None
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=20000),
    )


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
        :root {
            --ink: #14231d;
            --muted: #6a7d72;
            --paper: #f5f7f1;
            --lime: #c6ed59;
            --lime-deep: #7faf25;
            --line: rgba(20, 49, 34, .12);
            --glass: rgba(255, 255, 255, .73);
        }
        * { box-sizing: border-box; }
        html, body, [data-testid="stAppViewContainer"] { background: var(--paper); }
        body { color: var(--ink); font-family: 'DM Sans', sans-serif; }
        .stApp { background: radial-gradient(circle at 8% 0%, #e5f8dd 0, transparent 31%), radial-gradient(circle at 95% 22%, #fff0d4 0, transparent 26%), var(--paper); }
        .main .block-container { max-width: 1240px; padding: 32px 32px 72px; }
        #MainMenu, footer, [data-testid="stHeader"] { visibility: hidden; height: 0; }
        h1, h2, h3 { color: var(--ink) !important; font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -1px; }
        p, label, .stMarkdown { color: var(--ink); }
        .topbar { display:flex; align-items:center; justify-content:space-between; margin-bottom: 22px; }
        .brand { display:flex; gap:12px; align-items:center; }
        .brand-mark { width:44px; height:44px; display:grid; place-items:center; border-radius:15px; background:var(--ink); color:var(--lime); font-size:24px; box-shadow: 0 10px 24px rgba(20,35,29,.16); }
        .brand-name { font:700 20px 'Space Grotesk'; }
        .brand-sub { color:var(--muted); font-size:11px; letter-spacing:1.2px; text-transform:uppercase; }
        .live-pill { display:flex; align-items:center; gap:8px; padding:9px 13px; border:1px solid var(--line); border-radius:999px; background:rgba(255,255,255,.48); color:var(--muted); font-size:12px; }
        .live-dot { width:8px; height:8px; border-radius:50%; background:#76bb35; box-shadow:0 0 0 5px rgba(118,187,53,.13); animation:pulse 2s infinite; }
        @keyframes pulse { 50% { transform:scale(.72); opacity:.55; } }
        .hero { position:relative; min-height:330px; overflow:hidden; padding:44px 48px; border-radius:30px; background:linear-gradient(120deg, #17362a 0%, #234a30 52%, #617b34 100%); color:#f7fff4; box-shadow:0 24px 60px rgba(32,67,42,.2); }
        .hero:after { content:''; position:absolute; inset:auto -8% -52% 44%; height:330px; border:1px solid rgba(230,255,171,.35); border-radius:50%; transform:rotate(-18deg); box-shadow:0 0 0 32px rgba(230,255,171,.05), 0 0 0 64px rgba(230,255,171,.04); }
        .hero-copy { position:relative; z-index:2; max-width:660px; }
        .eyebrow { display:inline-flex; gap:8px; align-items:center; color:var(--lime); font-size:11px; font-weight:700; letter-spacing:1.7px; text-transform:uppercase; }
        .hero h1 { margin:18px 0 14px; color:#f8fff4 !important; font-size:clamp(42px, 6vw, 72px); line-height:.98; }
        .hero h1 span { color:var(--lime); }
        .hero p { max-width:570px; margin:0; color:rgba(245,255,241,.76); font-size:16px; line-height:1.65; }
        .hero-orbit { position:absolute; z-index:1; right:12%; top:45px; width:210px; height:210px; border:1px solid rgba(234,255,188,.25); border-radius:50%; animation:orbit 16s linear infinite; }
        .hero-orbit:before, .hero-orbit:after { content:'🥑'; position:absolute; display:grid; place-items:center; width:56px; height:56px; border-radius:18px; background:rgba(255,255,255,.13); backdrop-filter:blur(10px); font-size:27px; box-shadow:0 13px 25px rgba(0,0,0,.14); }
        .hero-orbit:before { top:-22px; left:70px; }
        .hero-orbit:after { right:-18px; bottom:16px; content:'🍓'; }
        @keyframes orbit { to { transform:rotate(360deg); } }
        .section-label { margin:28px 0 12px; color:var(--muted); font-size:11px; font-weight:700; letter-spacing:1.6px; text-transform:uppercase; }
        .welcome-card, .panel, .metric { border:1px solid rgba(255,255,255,.8); background:var(--glass); backdrop-filter:blur(18px); box-shadow:0 14px 35px rgba(41,68,47,.07); }
        .welcome-card { padding:26px; border-radius:24px; }
        .welcome-card h2 { margin:0 0 8px; font-size:28px; }
        .welcome-card p { margin:0; color:var(--muted); line-height:1.6; }
        .panel { padding:22px; border-radius:22px; }
        .panel-title { display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; font:700 17px 'Space Grotesk'; }
        .panel-title small { color:var(--muted); font:500 11px 'DM Sans'; }
        .drop-zone { padding:22px; border:1.5px dashed rgba(127,169,55,.45); border-radius:16px; background:linear-gradient(135deg, rgba(224,247,199,.55), rgba(255,255,255,.3)); color:var(--muted); text-align:center; }
        .drop-zone .drop-icon { font-size:34px; margin-bottom:6px; }
        .drop-zone strong { display:block; color:var(--ink); font-size:14px; }
        .drop-zone span { display:block; margin-top:4px; font-size:12px; }
        .metric-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; }
        .metric { position:relative; overflow:hidden; min-height:116px; padding:17px; border-radius:18px; transition:transform .25s ease, box-shadow .25s ease; }
        .metric:hover { transform:translateY(-4px); box-shadow:0 17px 30px rgba(41,68,47,.13); }
        .metric:after { content:''; position:absolute; right:-20px; bottom:-34px; width:90px; height:90px; border-radius:50%; background:rgba(198,237,89,.26); }
        .metric-label { color:var(--muted); font-size:11px; font-weight:700; letter-spacing:.9px; text-transform:uppercase; }
        .metric-value { margin-top:10px; font:700 28px 'Space Grotesk'; }
        .metric-note { color:var(--muted); font-size:11px; }
        .feature-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }
        .feature { padding:20px; border-radius:18px; background:#fff; border:1px solid var(--line); transition:transform .25s ease, border-color .25s ease, box-shadow .25s ease; }
        .feature:hover { transform:translateY(-5px) rotate(.3deg); border-color:rgba(127,169,55,.5); box-shadow:0 18px 30px rgba(41,68,47,.10); }
        .feature-icon { font-size:25px; }
        .feature strong { display:block; margin:12px 0 5px; font:700 15px 'Space Grotesk'; }
        .feature p { margin:0; color:var(--muted); font-size:13px; line-height:1.55; }
        .stTextInput label { color:var(--ink) !important; font-weight:700 !important; }
        .stTextInput input, [data-testid="stChatInput"] textarea { border:1px solid var(--line) !important; border-radius:14px !important; background:rgba(255,255,255,.7) !important; color:var(--ink) !important; }
        .stTextInput input:focus, [data-testid="stChatInput"]:focus-within { border-color:var(--lime-deep) !important; box-shadow:0 0 0 4px rgba(198,237,89,.22) !important; }
        .stButton > button, .stFormSubmitButton > button, [data-testid="stFormSubmitButton"] button { width:100%; min-height:46px; border:0; border-radius:13px; background:var(--ink) !important; color:#f7fff4 !important; font-family:'DM Sans', sans-serif !important; font-size:14px !important; font-weight:700 !important; -webkit-text-fill-color:#f7fff4 !important; transition:transform .2s ease, box-shadow .2s ease, background .2s ease; }
        .stButton > button p, .stFormSubmitButton > button p, [data-testid="stFormSubmitButton"] button p { color:#f7fff4 !important; font-family:'DM Sans', sans-serif !important; font-weight:700 !important; -webkit-text-fill-color:#f7fff4 !important; }
        .stButton > button:hover, .stFormSubmitButton > button:hover, [data-testid="stFormSubmitButton"] button:hover { transform:translateY(-2px); background:#31533e !important; box-shadow:0 12px 22px rgba(20,35,29,.18); color:#fff !important; }
        [data-testid="stChatMessage"] { border:1px solid var(--line); border-radius:18px; background:rgba(255,255,255,.68); box-shadow:0 8px 24px rgba(41,68,47,.05); animation:rise .4s ease both; }
        [data-testid="stChatMessage"] p { line-height:1.65; }
        @keyframes rise { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:none; } }
        .digest-note { color:var(--muted); font-size:13px; line-height:1.55; }
        .footer { margin-top:42px; color:var(--muted); font-size:12px; text-align:center; }
        @media (max-width: 800px) { .main .block-container { padding:18px 16px 48px; } .hero { min-height:360px; padding:30px 26px; border-radius:24px; } .hero h1 { font-size:48px; } .hero-orbit { right:-35px; top:145px; opacity:.65; } .metric-grid, .feature-grid { grid-template-columns:repeat(2,1fr); } .topbar { align-items:flex-start; } .live-pill { margin-top:3px; } }
        @media (max-width: 520px) { .metric-grid, .feature-grid { grid-template-columns:1fr; } .brand-sub { display:none; } .hero p { font-size:14px; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_interactions() -> None:
    components.html(
        """
        <script>
        (() => {
          try {
            const doc = window.parent.document;
            if (doc.getElementById('macrosnap-effects')) return;
            const style = doc.createElement('style');
            style.id = 'macrosnap-effects';
            style.textContent = `
              .ms-glow { position:fixed; width:260px; height:260px; border-radius:50%; pointer-events:none; z-index:999990; opacity:.18; filter:blur(45px); background:#c6ed59; transform:translate(-50%,-50%); transition:left .18s ease,top .18s ease,opacity .2s ease; }
              .ms-cursor-dot { position:fixed; width:10px; height:10px; border-radius:50%; pointer-events:none; z-index:1000000; background:#17362a; box-shadow:0 0 0 5px rgba(198,237,89,.32),0 0 22px rgba(127,175,37,.72); transform:translate(-50%,-50%); transition:transform .12s ease,background .15s ease; }
              .ms-cursor-ring { position:fixed; width:38px; height:38px; border:1px solid rgba(55,96,50,.52); border-radius:50%; pointer-events:none; z-index:999999; transform:translate(-50%,-50%); transition:width .2s ease,height .2s ease,border-color .2s ease,background .2s ease; }
              .ms-cursor-ring.is-hovering { width:62px; height:62px; border-color:#7faf25; background:rgba(198,237,89,.13); }
              .ms-cursor-ring.is-clicking { width:24px; height:24px; border-color:#ff9b62; background:rgba(255,155,98,.2); }
              .ms-particle { position:fixed; pointer-events:none; z-index:999991; font-size:18px; opacity:.28; animation:msFloat 8s ease-in-out infinite; }
              .ms-spark { position:fixed; pointer-events:none; z-index:1000001; font-size:16px; line-height:1; filter:drop-shadow(0 0 7px rgba(255,155,98,.5)); animation:msSpark .75s ease-out forwards; }
              @keyframes msSpark { from { opacity:1; transform:translate(0,0) rotate(0) scale(1); } to { opacity:0; transform:translate(var(--dx),var(--dy)) rotate(28deg) scale(.55); } }
              @keyframes msFloat { 0%,100% { transform:translateY(0) rotate(0); } 50% { transform:translateY(-24px) rotate(12deg); } }
            `;
            doc.head.appendChild(style);
                        const glow = doc.createElement('div'); glow.className = 'ms-glow'; glow.id = 'macrosnap-glow'; doc.body.appendChild(glow);
                        const dot = doc.createElement('div'); dot.className = 'ms-cursor-dot'; doc.body.appendChild(dot);
                        const ring = doc.createElement('div'); ring.className = 'ms-cursor-ring'; doc.body.appendChild(ring);
                        const trailFoods = ['🍋','🥑','🍓','🥕','🫐','🥬','🍊','🍎'];
            ['🍋','🥬','🫐','✦','🥕'].forEach((item, index) => { const node = doc.createElement('div'); node.className='ms-particle'; node.textContent=item; node.style.left=(8 + index*19)+'%'; node.style.top=(12 + (index%3)*27)+'%'; node.style.animationDelay=(index*.8)+'s'; doc.body.appendChild(node); });
                        let lastSpark = 0;
                        doc.addEventListener('mousemove', event => {
                            glow.style.left=event.clientX+'px'; glow.style.top=event.clientY+'px';
                            dot.style.left=event.clientX+'px'; dot.style.top=event.clientY+'px';
                            ring.style.left=event.clientX+'px'; ring.style.top=event.clientY+'px';
                            if (event.timeStamp - lastSpark > 90) {
                                lastSpark = event.timeStamp;
                                const spark = doc.createElement('div'); spark.className='ms-spark'; spark.textContent=trailFoods[Math.floor(Math.random()*trailFoods.length)];
                                spark.style.left=event.clientX+'px'; spark.style.top=event.clientY+'px';
                                spark.style.setProperty('--dx', ((Math.random()-.5)*24)+'px'); spark.style.setProperty('--dy', ((Math.random()-.5)*24)+'px');
                                doc.body.appendChild(spark); setTimeout(() => spark.remove(), 700);
                            }
                            const target = event.target.closest('button, input, textarea, [role="button"], .feature, .metric');
                            ring.classList.toggle('is-hovering', Boolean(target));
                        });
                        doc.addEventListener('mousedown', event => {
                            ring.classList.add('is-clicking'); dot.style.transform='translate(-50%,-50%) scale(1.7)';
                            for (let index=0; index<8; index++) {
                                const spark = doc.createElement('div'); spark.className='ms-spark'; spark.textContent=trailFoods[index % trailFoods.length]; spark.style.left=event.clientX+'px'; spark.style.top=event.clientY+'px';
                                spark.style.setProperty('--dx', Math.cos(index*Math.PI/4)*42+'px'); spark.style.setProperty('--dy', Math.sin(index*Math.PI/4)*42+'px'); doc.body.appendChild(spark); setTimeout(() => spark.remove(), 700);
                            }
                        });
                        doc.addEventListener('mouseup', () => { ring.classList.remove('is-clicking'); dot.style.transform='translate(-50%,-50%) scale(1)'; });
                        doc.addEventListener('mouseleave', () => { glow.style.opacity='.08'; dot.style.opacity='.3'; ring.style.opacity='.3'; });
                        doc.addEventListener('mouseenter', () => { glow.style.opacity='.18'; dot.style.opacity='1'; ring.style.opacity='1'; });
          } catch (error) { /* Presentation effects are optional. */ }
        })();
        </script>
        """,
        height=0,
    )


def render_topbar() -> None:
    user = st.session_state.name or "Your profile"
    render_html(f"""
        <div class="topbar">
          <div class="brand"><div class="brand-mark">🍋</div><div><div class="brand-name">MacroSnap</div><div class="brand-sub">AI nutrition intelligence</div></div></div>
          <div class="live-pill"><span class="live-dot"></span> Gemini analysis online <span>·</span> {user}</div>
        </div>
    """)


def render_hero() -> None:
    render_html("""
        <section class="hero">
          <div class="hero-copy">
            <div class="eyebrow">✦ Your food, decoded by AI</div>
            <h1>Eat with more<br><span>clarity.</span></h1>
            <p>Turn a meal photo or a quick question into friendly, useful nutrition intelligence. MacroSnap keeps the science simple and the next choice obvious.</p>
          </div>
          <div class="hero-orbit"></div>
        </section>
    """)


def render_features() -> None:
    render_html("""
        <div class="feature-grid">
          <div class="feature"><div class="feature-icon">📸</div><strong>Snap a meal</strong><p>Upload a photo from the chat composer and get an estimate of calories, protein, carbs and fat.</p></div>
          <div class="feature"><div class="feature-icon">🧠</div><strong>Ask naturally</strong><p>Talk to your nutrition buddy about portions, swaps, energy or what to eat next.</p></div>
          <div class="feature"><div class="feature-icon">📬</div><strong>Keep the signal</strong><p>Send a clean summary of your conversation to your inbox whenever you are ready.</p></div>
        </div>
    """)


def render_message(message: dict) -> None:
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.markdown(message["content"])
        else:
            st.image(message["content"], caption="Uploaded meal photo", use_container_width=True)


def add_message(role: str, kind: str, content) -> None:
    message = {"role": role, "kind": kind, "content": content}
    st.session_state.messages.append(message)
    render_message(message)


def ask_gemini(parts: list, max_retries: int = 2, output_placeholder=None) -> str:
    if st.session_state.chat is None:
        return "Chat session is not initialized. Please refresh the page and try again."
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response_text = ""
            for chunk in st.session_state.chat.send_message_stream(parts):
                chunk_text = getattr(chunk, "text", "") or ""
                if chunk_text:
                    response_text += chunk_text
                    if output_placeholder is not None:
                        output_placeholder.markdown(response_text)
            if not response_text:
                return "I couldn't generate a response. Please try again."
            return response_text
        except Exception as error:
            last_error = error
            error_text = str(error)
            transient = any(token in error_text.lower() for token in ("503", "unavailable", "high demand", "429", "resource_exhausted", "timeout", "timed out"))
            if transient and attempt < max_retries:
                time.sleep(1)
                continue
            break
    error_text = str(last_error)
    if "503" in error_text or "unavailable" in error_text.lower():
        return "⏳ Gemini is experiencing high demand right now. Please try again in a few seconds."
    if "429" in error_text or "resource_exhausted" in error_text.lower():
        return "⏳ Gemini's request limit was reached temporarily. Please try again shortly."
    if "timeout" in error_text.lower() or "timed out" in error_text.lower():
        return "⌛ Gemini took too long to respond. Please try again with a shorter question or a smaller image."
    return f"Sorry, something went wrong while communicating with Gemini.\n\n{error_text}"


def is_gemini_error(response: str) -> bool:
    error_prefixes = ("Sorry", "⏳", "⌛", "Chat session is not initialized", "I couldn't")
    return response.startswith(error_prefixes)


def show_onboarding(gemini_client) -> None:
    render_topbar()
    render_hero()
    st.markdown('<div class="section-label">Start with your profile</div>', unsafe_allow_html=True)
    with st.form("onboarding_form"):
        st.markdown('<div class="welcome-card"><h2>A smarter food log starts here.</h2><p>Tell us where to send your daily digest, then your AI nutrition workspace will be ready in one click.</p></div>', unsafe_allow_html=True)
        st.write("")
        left, right = st.columns(2)
        with left:
            name = st.text_input("Your name", placeholder="e.g. Pooja")
        with right:
            email = st.text_input("Email address", placeholder="you@example.com")
        submitted = st.form_submit_button("Open my nutrition workspace →")
    if not submitted:
        st.markdown('<div class="section-label">What you can do next</div>', unsafe_allow_html=True)
        render_features()
        return
    clean_name = name.strip()
    clean_email = email.strip()
    if not clean_name:
        st.error("Please enter your name.")
        return
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", clean_email):
        st.error("Please enter a valid email address.")
        return
    if gemini_client is None:
        st.error("Gemini API key is missing. Add GEMINI_API_KEY to Streamlit secrets.")
        return
    try:
        st.session_state.name = clean_name
        st.session_state.email = clean_email
        st.session_state.chat = gemini_client.chats.create(model=MODEL_NAME, config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT))
        st.session_state.messages = []
        st.session_state.active_model = MODEL_NAME
        st.session_state.onboarded = True
        st.rerun()
    except Exception as error:
        st.error("Unable to initialize MacroSnap right now.")
        st.code(str(error))


def render_metrics() -> None:
    message_count = len(st.session_state.messages)
    meal_count = sum(1 for message in st.session_state.messages if message["kind"] == "image")
    render_html(f"""
        <div class="metric-grid">
          <div class="metric"><div class="metric-label">Meals scanned</div><div class="metric-value">{meal_count:02d}</div><div class="metric-note">photo insights</div></div>
          <div class="metric"><div class="metric-label">Conversation</div><div class="metric-value">{message_count:02d}</div><div class="metric-note">signals captured</div></div>
          <div class="metric"><div class="metric-label">AI mode</div><div class="metric-value">Live</div><div class="metric-note">Gemini powered</div></div>
          <div class="metric"><div class="metric-label">Digest</div><div class="metric-value">Ready</div><div class="metric-note">whenever you are</div></div>
        </div>
    """)


def handle_chat() -> None:
    user_input = st.chat_input("Ask about a meal, or attach a photo...", accept_file=True, file_type=["jpg", "jpeg", "png"])
    if user_input is None:
        return
    text_input = user_input.text if hasattr(user_input, "text") else (user_input if isinstance(user_input, str) else "")
    files = user_input.files if hasattr(user_input, "files") else []
    photo = files[0] if files else None
    parts = []
    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))
    if text_input and text_input.strip():
        clean_text = text_input.strip()
        add_message("user", "text", clean_text)
        parts.append(clean_text)
    if photo is not None and not (text_input and text_input.strip()):
        parts.append("Analyze this meal. Identify the likely foods, estimated calories, protein, carbohydrates, fat, portion assumptions, and one practical nutrition insight. Clearly state that all values are estimates.")
    if not parts:
        return
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_placeholder.caption("Gemini is reading your meal...")
        answer = ask_gemini(parts, output_placeholder=response_placeholder)
        response_placeholder.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "kind": "text", "content": answer})


def render_digest() -> None:
    st.markdown('<div class="section-label">Your nutrition digest</div>', unsafe_allow_html=True)
    left, right = st.columns([1.6, 1], gap="large")
    with left:
        st.markdown('<div class="panel"><div class="panel-title">Send the signal to your inbox <small>plain + formatted email</small></div><div class="digest-note">MacroSnap will summarize every meal and question in this conversation into a concise, useful digest.</div></div>', unsafe_allow_html=True)
    with right:
        enough_messages = len(st.session_state.messages) > 2
        if st.button("📬 Send digest to email", disabled=not enough_messages, key="send_digest_button"):
            if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
                st.error("Email service is not configured. Add GMAIL_ADDRESS and GMAIL_APP_PASSWORD to Streamlit secrets.")
                return
            with st.spinner("Preparing your nutrition digest..."):
                summary = ask_gemini([SUMMARY_REQUEST_PROMPT])
            if is_gemini_error(summary):
                st.error(summary)
                return
            success, message = send_email_digest(
                st.session_state.email,
                st.session_state.name,
                summary,
                GMAIL_ADDRESS,
                GMAIL_APP_PASSWORD,
                MACROSNAP_URL,
            )
            if success:
                st.success(message)
            else:
                st.error(message)


def main() -> None:
    init_state()
    inject_css()
    inject_interactions()
    gemini_client = get_gemini_client(GEMINI_API_KEY)
    if not st.session_state.onboarded:
        show_onboarding(gemini_client)
        st.stop()
    render_topbar()
    if st.session_state.chat is None or st.session_state.active_model != MODEL_NAME:
        if gemini_client is not None:
            try:
                st.session_state.chat = gemini_client.chats.create(model=MODEL_NAME, config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT))
                st.session_state.active_model = MODEL_NAME
            except Exception as error:
                st.error(f"Could not initialize Gemini: {error}")
    render_metrics()
    st.markdown('<div class="section-label">Your AI nutrition desk</div>', unsafe_allow_html=True)
    left, right = st.columns([1.55, 1], gap="large")
    with left:
        if not st.session_state.messages:
            render_html('<div class="panel"><div class="panel-title">Ready when you are <small>chat + photo analysis</small></div><div class="drop-zone"><div class="drop-icon">📸</div><strong>Drop a meal into the chat below</strong><span>JPG and PNG supported · estimates in seconds</span></div></div>')
        for message in st.session_state.messages:
            render_message(message)
        if not st.session_state.messages:
            add_message("assistant", "text", WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name))
        handle_chat()
    with right:
        render_features()
    if len(st.session_state.messages) > 0:
        render_digest()
    render_html('<div class="footer">MacroSnap · AI-powered nutrition insights for everyday meals · Powered by Google Gemini</div>')


main()
