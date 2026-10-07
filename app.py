import time
import streamlit as st
from google import genai
from google.genai import types

from email_service import send_email_digest
from prompts import SUMMARY_REQUEST_PROMPT, SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE

# --- Page Configuration ---
st.set_page_config(
    page_title="MacroSnap - AI Nutrition Buddy",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Configuration & Secrets Loading ---
DEFAULT_MODEL = "gemini-3.8-flash"
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
MODEL_NAME = st.secrets.get("GEMINI_MODEL", DEFAULT_MODEL)
GMAIL_ADDRESS = st.secrets.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = st.secrets.get("GMAIL_APP_PASSWORD", "")


# --- Cached Gemini Client ---
@st.cache_resource
def get_gemini_client(api_key: str):
    """
    Initializes and caches the Google GenAI client instance.
    Caching prevents client reconnection overhead across Streamlit reruns.
    """
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


# Initialize client
gemini_client = get_gemini_client(GEMINI_API_KEY)


def render_message(message: dict):
    """Renders a single chat message (text or image) in the Streamlit chat view."""
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"], caption="Uploaded Meal Photo", use_container_width=True)


def add_message(role: str, kind: str, content):
    """Appends a message to session state and immediately renders it."""
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])


def ask_gemini(parts: list, max_retries: int = 3) -> str:
    """
    Sends prompt parts (text and/or image bytes) to the active Gemini chat session.
    Implements automatic exponential backoff retry for transient 503 (high demand) and 429 errors.
    """
    if "chat" not in st.session_state or st.session_state.chat is None:
        return "Chat session is not initialized. Please refresh and onboard again."

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = st.session_state.chat.send_message(parts)
            return response.text
        except Exception as error:
            last_error = error
            error_msg = str(error)
            # Detect transient server overload / rate-limit conditions
            is_transient = (
                "503" in error_msg
                or "UNAVAILABLE" in error_msg
                or "high demand" in error_msg.lower()
                or "429" in error_msg
                or "resource_exhausted" in error_msg.lower()
            )
            if is_transient and attempt < max_retries:
                time.sleep(attempt * 2)  # backoff: 2s, 4s
                continue
            break

    error_text = str(last_error)
    if "503" in error_text or "UNAVAILABLE" in error_text:
        return (
            "⏳ **Google Gemini is currently experiencing high demand.** "
            "Traffic spikes usually clear within a few moments. Please wait 5–10 seconds and try your request again!"
        )
    return f"Sorry, something went wrong while communicating with Gemini: {last_error}"


# ==========================================
# STEP 1: ONBOARDING SCREEN
# ==========================================
if "onboarded" not in st.session_state or not st.session_state.onboarded:
    st.title("🥗 MacroSnap")
    st.subheader("Snap it. Track it. Receive your nutrition digest.")
    st.caption("AI-powered multimodal calorie & macro estimation powered by Google Gemini.")

    # Check for missing API keys
    if not GEMINI_API_KEY:
        st.warning(
            "⚠️ **Gemini API Key missing!** Please add `GEMINI_API_KEY` to your `.streamlit/secrets.toml` file."
        )

    with st.form("onboarding_form"):
        name = st.text_input("Your Name", placeholder="e.g. Alex Sharma")
        email = st.text_input(
            "Your Email Address",
            placeholder="alex@example.com",
            help="MacroSnap will send your daily nutrition digest to this email address.",
        )
        submitted = st.form_submit_button("Let's go 🚀", use_container_width=True)

    if submitted:
        if not name.strip() or not email.strip():
            st.warning("Please fill in both your name and email address.")
        elif "@" not in email or "." not in email:
            st.warning("Please enter a valid email address.")
        elif not GEMINI_API_KEY:
            st.error("Cannot start chat: GEMINI_API_KEY is not set in secrets.toml.")
        else:
            try:
                st.session_state.name = name.strip()
                st.session_state.email = email.strip()
                st.session_state.chat = gemini_client.chats.create(
                    model=MODEL_NAME,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                )
                st.session_state.messages = []
                st.session_state.onboarded = True
                st.rerun()
            except Exception as e:
                st.error(f"Failed to initialize Gemini chat session: {e}")

    st.stop()


# ==========================================
# STEP 2: CHAT & NUTRITION DASHBOARD
# ==========================================
# Seamlessly recreate chat session if API key or model was updated in secrets.toml
if (
    st.session_state.get("active_api_key") != GEMINI_API_KEY
    or st.session_state.get("active_model") != MODEL_NAME
):
    if gemini_client:
        try:
            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            )
            st.session_state.active_api_key = GEMINI_API_KEY
            st.session_state.active_model = MODEL_NAME
        except Exception as e:
            st.error(f"Failed to bind updated Gemini model/key: {e}")

header_col, action_col = st.columns([5, 3], vertical_alignment="center")

with header_col:
    st.title("🥗 MacroSnap")
    st.caption(f"Logged in as **{st.session_state.name}** • Digest recipient: `{st.session_state.email}`")

with action_col:
    # Disable send button until at least one user-assistant exchange exists
    send_disabled = len(st.session_state.messages) <= 2
    button_tooltip = "Log at least one meal to enable digest export" if send_disabled else "Send summary to email"
    
    if st.button("📤 Send Digest to Email", disabled=send_disabled, use_container_width=True, help=button_tooltip):
        with st.spinner("Summarizing your nutritional intake..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])
        
        with st.spinner("Dispatching email digest via SMTP..."):
            success, info = send_email_digest(
                to_address=st.session_state.email,
                user_name=st.session_state.name,
                summary_text=summary,
                gmail_address=GMAIL_ADDRESS,
                gmail_app_password=GMAIL_APP_PASSWORD,
            )
        
        if success:
            st.success("✅ Digest sent! Check your inbox 📬")
        else:
            st.error(f"❌ Failed to send digest: {info}")

st.divider()

# Display Welcome Message if new conversation
if not st.session_state.messages:
    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name),
    )
else:
    for message in st.session_state.messages:
        render_message(message)

# Chat Input supporting both text queries and meal photo attachments
user_input = st.chat_input(
    "Ask a nutrition question, or attach a photo of your meal...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))

    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        # Implicit prompt if user uploads a photo without typing text
        parts.append("What is this meal? Give me the estimated calories and macros (protein, carbs, fat).")

    with st.spinner("Crunching the numbers..."):
        answer = ask_gemini(parts)

    add_message("assistant", "text", answer)
