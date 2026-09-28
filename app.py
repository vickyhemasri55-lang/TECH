import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types

from chatbot_config import BOT_NAME, MODEL_NAME, SYSTEM_PROMPT, WELCOME_MESSAGE

load_dotenv()

app = Flask(__name__)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MAX_HISTORY = 20


def build_contents(history, message):
    contents = []
    for item in history[-MAX_HISTORY:]:
        role = "user" if item.get("role") == "user" else "model"
        text = str(item.get("text", "")).strip()
        if text:
            contents.append(types.Content(role=role, parts=[types.Part(text=text)]))
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))
    return contents


@app.route("/")
def index():
    return render_template("index.html", bot_name=BOT_NAME, welcome=WELCOME_MESSAGE)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "Please type a message."}), 400

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=build_contents(history, message),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.6,
            ),
        )
        return jsonify({"reply": response.text or "I could not generate a reply."})
    except Exception:
        return jsonify({"error": "Something went wrong. Please try again."}), 500


if __name__ == "__main__":
    app.run(debug=True)
