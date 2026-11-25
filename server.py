import os
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI

app = Flask(__name__, static_folder=".")

SYSTEM_PROMPT = """You are XODEQ AI Technical Service & Support Assistant for industrial machines and automation.
Support topics: servo motors/drives, CNC controllers, CNC routers, fiber laser cutting machines,
PLC/automation, motion control, pulse-direction systems, wiring, communications, and alarm diagnosis.

Guidelines:
- Respond in the same language as the user's question (Gujarati, Hindi, or English).
- Give practical, organized troubleshooting steps and explain what each step checks.
- Ask for brand/model, exact alarm code, machine symptoms, and context when needed.
- Never guess manufacturer-specific parameters, wiring pinouts, alarm meanings, or values. State when the manual is needed.
- Start with safe checks. Warn users to isolate power before inspecting wiring.
- Never instruct unqualified users to open energized or high-voltage equipment. Recommend a qualified technician.
- Do not advise bypassing safety circuits, interlocks, emergency stops, or protective devices.
- Distinguish likely causes from confirmed facts and ask targeted follow-up questions.
- Use headings and numbered steps when useful; avoid generic answers when details are available.
"""

@app.get("/")
def home():
    return send_from_directory(".", "index.html")



@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])

    if not isinstance(messages, list) or not messages:
        return jsonify({"error": "Please enter a technical question."}), 400

    clean_messages = []
    for msg in messages[-20:]:
        if isinstance(msg, dict) and msg.get("role") in ("user", "assistant") and isinstance(msg.get("content"), str):
            clean_messages.append({"role": msg["role"], "content": msg["content"][:12000]})

    if not clean_messages:
        return jsonify({"error": "No valid chat messages were provided."}), 400

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return jsonify({"error": "AI service is not configured. Set OPENAI_API_KEY in Render Environment Variables."}), 503

    try:
        client = OpenAI(api_key=api_key)
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + clean_messages,
            temperature=0.3,
            max_tokens=1200,
        )
        reply = response.choices[0].message.content or "I couldn't generate a response. Please try again."
        return jsonify({"reply": reply})
    except Exception as exc:
        print(f"AI request failed: {type(exc).__name__}: {exc}")
        return jsonify({"error": "AI request failed. Check Render logs, OpenAI API key, billing/credits, and model access."}), 502


@app.get("/health")
def health():
    return jsonify({"status": "XODEQ AI Support is running", "ai_configured": bool(os.environ.get("OPENAI_API_KEY"))})



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
