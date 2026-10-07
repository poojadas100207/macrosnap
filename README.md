# 🥗 MacroSnap — Multimodal AI Nutrition & Calorie Intelligence Agent

> **An end-to-end multimodal AI application that analyzes meal photos or descriptions in real-time, estimates calories and macronutrients using Google Gemini, and delivers personalized daily nutrition digests directly to your email inbox.**

---

## 📌 Executive Summary

Traditional diet-tracking applications (like MyFitnessPal or Cronometer) suffer from high user drop-off due to tedious manual search and portion logging. **MacroSnap** solves this problem by pairing **Google Gemini's Multimodal Vision API** with an interactive **Streamlit** chat interface and an automated **Gmail SMTP** notification engine. 

Users simply take a picture of their meal or type a quick query. MacroSnap identifies the food items, provides rough caloric and macronutrient breakdowns (Protein, Carbohydrates, Fats), and compiles the day's meals into a structured digest sent directly to the user's inbox with a single click.

---

## 🚀 Key Highlights & Architecture

```mermaid
flowchart TD
    A[User Meal Photo / Query] --> B[Streamlit Reactive Web App]
    B --> C{Multimodal Input Handler}
    C -->|Image Bytes + MIME| D[Gemini 3.8 Flash Vision]
    C -->|Text Query| D
    D --> E[Conversational Session Memory & System Guardrails]
    E --> F[Instant Macro Breakdown UI]
    F --> G[End of Day: Request Digest]
    G --> H[Gemini Nutrition Summarizer]
    H --> I[Gmail SMTP Engine (SSL 465)]
    I --> J[User Email Inbox 📬]
```

### Core Capabilities:
- **Zero-Shot Multimodal Recognition:** Ingests raw camera image bytes (`jpg`, `jpeg`, `png`) and identifies complex, mixed-dish meals without training custom classifiers.
- **Strict Guardrailed Persona:** Engineered system instructions enforce that conversations stay strictly on food, fitness, and nutrition while declining off-topic queries.
- **Conversational Memory:** Preserves multi-turn context (e.g., asking *"How much protein was in that earlier bowl?"*) within an active Gemini chat session.
- **100% Free Notification Pipeline:** Eliminates expensive third-party SMS/WhatsApp gateways by utilizing Python's native `smtplib` over secure SSL to dispatch responsive HTML and plain-text digests.
- **Session-Safe Client Caching:** Utilizes `@st.cache_resource` connection pooling to maintain alive API client sessions across Streamlit's reactive re-runs.

---

## 🎓 Resume & Portfolio Showcase (For AI/ML Students)

If you are showcasing this project on your resume or in technical interviews, you can use the following tailored bullet points:

### 📄 Resume Bullet Points (STAR Format)
- **Engineered an end-to-end multimodal nutrition tracking agent** using Google Gemini 3.8 Flash and Streamlit, enabling zero-shot food recognition and instant caloric/macronutrient breakdown from meal photographs.
- **Architected a multi-turn conversational session pipeline** with strict prompt guardrails, handling in-memory image byte serialization and maintaining contextual chat history across application re-renders.
- **Developed an automated notification microservice** using Python's `smtplib` and MIME multipart formatting, delivering formatted daily nutritional digests via Gmail SMTP with zero external API costs.
- **Optimized client instantiation and state management** leveraging Streamlit caching (`@st.cache_resource`), mitigating redundant connection overhead and eliminating socket closure anomalies.

### 💡 Tech Stack
- **Languages & Frameworks:** Python 3.10+, Streamlit
- **AI & Computer Vision:** Google Gemini 3.8 Flash (`google-genai` SDK), Multimodal Prompt Engineering
- **Networking & Protocols:** SMTP SSL, MIME Multipart Email Protocols
- **State & Architecture:** Streamlit Session State, Connection Pooling, Git

---

## 🛠️ Project Structure

```text
macrosnap/
├── app.py                      # Main Streamlit web application & UI workflow
├── prompts.py                  # Guardrailed system prompts, persona & summary prompt
├── email_service.py            # SMTP dispatch service with HTML/Plain-text formatting
├── requirements.txt            # Minimal, lightweight dependencies
├── .gitignore                  # Prevents committing secrets.toml, venv, and cache
├── README.md                   # Project documentation & resume guide
└── .streamlit/
    └── secrets.toml.example    # Configuration template for API keys & credentials
```

---

## ⚡ Quickstart Guide (Local Setup)

### 1. Clone & Navigate to Project
```bash
git clone <your-repo-url>
cd macrosnap
```

### 2. Set Up Virtual Environment
```bash
# Windows PowerShell:
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux:
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Secrets
1. Create a copy of the secrets template:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
2. Open `.streamlit/secrets.toml` and fill in:
   - **`GEMINI_API_KEY`**: Get a free API key from [Google AI Studio](https://aistudio.google.com).
   - **`GMAIL_ADDRESS`**: Your Gmail account address.
   - **`GMAIL_APP_PASSWORD`**: A 16-character Google App Password:
     1. Visit your [Google Security Settings](https://myaccount.google.com/security).
     2. Ensure **2-Step Verification** is turned ON.
     3. Search for or navigate to **App passwords** ([direct link](https://myaccount.google.com/apppasswords)).
     4. Generate an app password for "MacroSnap" and paste the 16 characters into `secrets.toml`.

> ⚠️ **CRITICAL SECURITY NOTE:** Never commit `.streamlit/secrets.toml` with real credentials to GitHub. It is already included in `.gitignore`.

### 5. Run the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🌐 Deployment to Streamlit Community Cloud

1. Push your repository to GitHub (ensure `.streamlit/secrets.toml` is NOT committed).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **"New app"**, select your repository, branch, and set `app.py` as the entry point.
4. In **Advanced Settings → Secrets**, paste the exact keys and values from your local `.streamlit/secrets.toml`:
   ```toml
   GEMINI_API_KEY = "your-actual-api-key"
   GEMINI_MODEL = "gemini-3.8-flash"
   GMAIL_ADDRESS = "your-email@gmail.com"
   GMAIL_APP_PASSWORD = "your-16-char-app-password"
   ```
5. Click **Deploy**. Your app is now live with a public URL!

---

## 📝 Evaluation & Submission Checklist
- [x] Functional multimodal image + text processing
- [x] Guardrailed system prompt scoping conversational agent to nutrition only
- [x] Automated single-click email digest delivery
- [x] Secrets isolated in `.streamlit/secrets.toml` and excluded in `.gitignore`
- [x] Clear installation instructions and resume highlights

---

## 📄 License
This project is open-source under the MIT License.
