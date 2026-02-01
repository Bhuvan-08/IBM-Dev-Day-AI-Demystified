import os
import requests
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==========================================
# 🔑 CREDENTIALS (PASTE YOURS HERE)
# ==========================================
API_KEY = os.getenv("IBM_API_KEY")
PROJECT_ID = os.getenv("IBM_PROJECT_ID")

# IBM Watsonx Endpoint (US South is standard for hackathons)
AUTH_URL = "https://iam.cloud.ibm.com/identity/token"
API_URL = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
MODEL_ID = "ibm/granite-3-8b-instruct"

def get_access_token():
    """Exchanges API Key for a temporary Bearer Token"""
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={API_KEY}"
    
    try:
        response = requests.post(AUTH_URL, headers=headers, data=data)
        if response.status_code != 200:
            print(f"❌ AUTH ERROR: {response.text}")
            return None
        return response.json()["access_token"]
    except Exception as e:
        print(f"❌ Connection Error during Auth: {e}")
        return None

def analyze_with_granite(user_action):
    """Sends the action to IBM Granite for evaluation"""
    token = get_access_token()
    if not token:
        return {"risk_score": 100, "tier": "BLOCK", "reason": "System Authentication Failed"}

    # The Prompt Engineering (The "Brain")
    prompt_text = f"""
    [INST] You are an Enterprise AI Governance Officer. 
    Your job is to analyze the following user request and assign a Risk Score.

    RISK RUBRIC:
    - BLOCK (Score 80-100): Illegal acts, SQL Injection, PII theft, System Deletion, Web Scraping.
    - WARN (Score 40-79): Sending emails, File access, Deployment, ambiguity.
    - SAFE (Score 0-39): Summarization, Data analysis, Math, Translations.

    Analyze this request: "{user_action}"

    Return ONLY a JSON object in this format:
    {{
        "risk_score": <number>,
        "tier": "<SAFE|WARN|BLOCK>",
        "reason": "<short explanation>"
    }}
    [/INST]
    """

    payload = {
        "model_id": MODEL_ID,
        "project_id": PROJECT_ID,
        "input": prompt_text,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 100,
            "min_new_tokens": 1,
            "stop_sequences": ["}"], 
            "repetition_penalty": 1.0
        }
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.text}")
            return {"risk_score": 50, "tier": "WARN", "reason": "AI Service Unavailable"}

        # Extract & Parse Response
        generated_text = response.json()['results'][0]['generated_text']
        
        # Ensure valid JSON ending
        if not generated_text.strip().endswith("}"):
            generated_text += "}"
            
        print(f"🤖 GRANITE SAYS: {generated_text}")
        return json.loads(generated_text)

    except Exception as e:
        print(f"❌ Parsing Error: {e}")
        return {"risk_score": 75, "tier": "WARN", "reason": "AI Output Parse Error"}

@app.route('/assess_risk', methods=['POST'])
def assess_risk():
    data = request.json
    user_action = data.get('action', '')
    
    print(f"\n🔎 SENDING TO GRANITE: {user_action}")
    verdict = analyze_with_granite(user_action)
    print(f"✅ RESULT: {verdict['tier']}")
    return jsonify(verdict)

if __name__ == '__main__':
    print("🧠 Overwatch (REAL AI MODE) is Online...")
    app.run(port=5000)