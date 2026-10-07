# 🥗 MacroSnap - AI Nutrition Buddy

> An AI-powered nutrition tracking application that analyzes meal photos and descriptions, estimates calories and macronutrients using Google Gemini, and delivers personalized nutrition summaries via email.

## Overview

MacroSnap is a multimodal nutrition tracking assistant built with Streamlit and Google Gemini. Users can upload a food image or describe a meal in natural language to receive calorie estimates, macronutrient breakdowns, and nutrition insights.

The application combines image understanding, conversational AI, and email-based reporting to simplify meal tracking without requiring manual food searches or logging.

## 🚀 Key Features

- 📷 Analyze food images using Gemini's multimodal capabilities
- 💬 Ask nutrition-related questions through a conversational interface
- 🔢 Estimate calories, protein, carbohydrates, and fats
- 📈 Generate personalized nutrition insights
- 📧 Receive daily nutrition summaries via email
- 🛡️ Nutrition-focused AI assistant with guardrails for safe interactions

## 🏗️ Architecture

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

## 💡 Core Capabilities

- **Food Image Analysis:** Accepts meal photos (`jpg`, `jpeg`, `png`) and uses Google Gemini to identify food items and estimate nutritional information.
- **Nutrition-Focused Assistant:** Restricts conversations to nutrition, fitness, and healthy eating topics through prompt guardrails.
- **Conversational Memory:** Maintains context across interactions using Streamlit session state, allowing users to ask follow-up questions about previous meals.
- **Email Nutrition Reports:** Generates and sends daily nutrition summaries through Gmail SMTP using secure SSL connections.
- **Efficient Resource Management:** Uses `@st.cache_resource` to reuse API clients and improve application performance across Streamlit reruns.

---

## 💡 Tech Stack

- **Programming Language:** Python 3.10+
- **Frontend & UI:** Streamlit
- **AI & Vision:** Google Gemini API (`google-genai`)
- **Email Service:** Gmail SMTP (`smtplib`, MIME)
- **State Management:** Streamlit Session State
- **Version Control:** Git & GitHub

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
## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/poojadas100207/macrosnap.git
cd macrosnap
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Secrets

Create `.streamlit/secrets.toml` using the template:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Add your credentials:

```toml
GEMINI_API_KEY = "your-api-key"
GMAIL_ADDRESS = "your-email@gmail.com"
GMAIL_APP_PASSWORD = "your-app-password"
```

- Get a Gemini API key from: https://aistudio.google.com
- Generate a Gmail App Password from: https://myaccount.google.com/apppasswords

> ⚠️ Never commit `.streamlit/secrets.toml` to GitHub. The file contains sensitive credentials and should remain private.

### 5. Run the Application

```bash
streamlit run app.py
```

Open:

```
http://localhost:8501
```

## 🌐 Deployment

### Streamlit Community Cloud

1. Push the project to GitHub.
2. Sign in to Streamlit Community Cloud.
3. Create a new app and select this repository.
4. Add the following secrets in App Settings:

```toml
GEMINI_API_KEY = "your-api-key"
GMAIL_ADDRESS = "your-email@gmail.com"
GMAIL_APP_PASSWORD = "your-app-password"


## 📄 License
This project is open-source under the MIT License.
