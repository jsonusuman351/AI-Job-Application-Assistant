# 🚀 AI Job Application Assistant (Powered by LangGraph)

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python) ![LangGraph](https://img.shields.io/badge/LangGraph-Stateful_Agent-FF4B4B?style=for-the-badge) ![LangChain](https://img.shields.io/badge/LangChain-0086CB?style=for-the-badge&logo=langchain) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)

Welcome to the **AI Job Application Assistant**.
Job hunting is exhausting. Instead of writing generic emails manually, I built an **Autonomous Agent** to do the heavy lifting for me.

This full-stack application acts as my personal recruiter. I simply **upload my resume** and **paste the job description**, and the AI takes over. It researches the company online, drafts a highly personalized cold email, and—after my approval—**actually sends the email** with my resume attached.

---

### 🎯 The Objective

The goal was to build an agent that doesn't just write text, but **takes action**.

* **The Problem:** Writing tailored emails for every job application is time-consuming.
* **The Solution:** I engineered a **LangGraph Agent** that:
    1.  **Analyzes** the Job Description (JD) I manually provide against my Resume.
    2.  **Searches the Web** (using Tavily API) to find the company's latest news, mission, or projects.
    3.  **Drafts** a researched, human-like email that mentions specific company details.
    4.  **Sends** the email directly to the recruiter via SMTP.

---

### 📸 Application Walkthrough

Here is the actual workflow of the agent in action:

#### 1. Input: Resume & Job Description
*I start by uploading my PDF resume and manually pasting the Job Description text. This gives the AI the exact context it needs.*

#### 2. Research & Drafting
*The Agent goes online to **search for the company** mentioned in the JD. It uses this info to draft a personalized email. It then pauses for my review (Human-in-the-Loop).*

#### 3. Final Action: Email Sent
*Once I approve the draft and provide the recruiter's email, the Agent automatically sends the email with my resume attached.*

---

### ✨ Core Features

1.  **Stateful Agent Workflow (LangGraph)**:
    * Unlike a simple chatbot, this system maintains a "state" (Resume -> JD -> Draft -> Feedback) throughout the conversation.

2.  **Automated Web Research**:
    * The agent uses the **Tavily Search API** (`web_search` tool) to find live information about the company. This ensures the cover letter sounds genuine and well-researched, not generic.

3.  **Manual JD Handling**:
    * To ensure accuracy, the system accepts the Job Description as direct text input, avoiding parsing errors from external URLs.

4.  **Email Automation (SMTP)**:
    * The system integrates with Python's `smtplib`. It constructs a professional email with the PDF resume attached and sends it securely.

---

### 🛠️ Tech Stack

* **Orchestration:** LangChain & LangGraph (Cyclic Agent Flow)
* **Backend:** FastAPI (Asynchronous API)
* **Frontend:** Streamlit (Interactive UI)
* **LLM:** OpenAI GPT-4o (Reasoning & Drafting)
* **Tools:** Tavily API (Web Search) & SMTP (Email Sending)

---

### ⚙️ Setup and Installation

The project is split into a Backend API and a Frontend App.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/ai-job-application-assistant.git](https://github.com/your-username/ai-job-application-assistant.git)
    ```

2.  **Backend Setup (FastAPI):**
    ```bash
    cd api
    pip install -r requirements.txt
    # Create a .env file with: OPENAI_API_KEY, TAVILY_API_KEY, SENDER_EMAIL, GMAIL_APP_PASSWORD
    uvicorn main:app --reload --port 8000
    ```

3.  **Frontend Setup (Streamlit):**
    ```bash
    cd ../app
    pip install -r requirements.txt
    streamlit run streamlit_app.py
    ```

---

### 🔬 Project Structure

* **`api/agent_logic.py`**: Defines the LangGraph StateGraph, nodes, and the system prompt that guides the agent's research and drafting behavior.
* **`api/tools.py`**: Contains the `web_search` tool (Tavily) and `send_email` tool.
* **`app/streamlit_app.py`**: Handles the UI where users upload resumes and paste JDs.

---
