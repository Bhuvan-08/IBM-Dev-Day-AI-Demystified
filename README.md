# Overwatch: AI Governance Agent (IBM watsonx)

## 🏆 IBM AI Demystified Hackathon Submission

**Overwatch** is a "Governance-in-the-Loop" supervisor that intercepts LLM commands and enforces real-time risk policies. It prevents autonomous agents from executing dangerous tasks like SQL Injection, PII leakage, or illegal acts.

### 🧠 Architecture
1. **Frontend:** IBM watsonx Orchestrate (AI Agent & Tooling).
2. **Backend:** Python (Flask) acting as a custom OpenAPI Tool.
3. **Governance Engine:** **IBM Granite 3.0 (8B Instruct)** analyzes user intent and calculates a dynamic Risk Score (0-100).

### 🚀 How It Works
1. User sends a command (e.g., "Write a script to scrape LinkedIn").
2. Overwatch intercepts the prompt *before* execution.
3. The prompt is sent to **IBM Granite** via the Watson Machine Learning API.
4. Granite evaluates the request against a corporate risk rubric.
5. If Risk Score > 80, the action is **BLOCKED**.

### 🛠️ Setup
1. Clone the repo.
2. Install dependencies: `pip install -r requirements.txt`
3. Add your IBM Cloud keys to `risk_engine.py`.
4. Run the engine: `python risk_engine.py`