import os
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI

app = Flask(__name__, static_folder=".")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are XODEQ AI Technical Support Assistant.

You provide technical support for:
- Servo Motors and Servo Drives
- CNC Controllers
- Fiber Laser Cutting Machines
- CNC Router Machines
- Automation and Motion Control
- Pulse and Direction systems
- Wiring and communication troubleshooting
- Alarm diagnosis

Rules:
1. Give clear, practical technical answers.
2. Ask for model number and alarm code when needed.
3. Explain step-by-step troubleshooting.
4. Prioritize electrical and machine safety.
5. Never invent manufacturer-specific parameters.
6. Support Gujarati, Hindi, and English.
7. If information is insufficient, ask for details.
8. Do not recommend opening high-voltage equipment without a qualified engineer.
"""

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        messages = data.get("messages", [])

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *messages
            ],
            temperature=0.3
        )

        return jsonify({
            "reply": response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return {"status": "XODEQ AI Support is running"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
