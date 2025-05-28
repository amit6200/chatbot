
from flask import Flask, render_template, request, jsonify
import requests
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder="template")

# Your OpenRouter API key (use env var or replace below)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    # Get message text and uploaded file from form-data
    user_input = request.form.get("message", "").strip()
    uploaded_file = request.files.get("file")

    if not user_input and not uploaded_file:
        return jsonify({"error": "No message or file provided"}), 400

    # Optional: Save uploaded file if needed
    if uploaded_file:
        filename = secure_filename(uploaded_file.filename)
        save_path = os.path.join("uploads", filename)
        # Make sure uploads folder exists
        os.makedirs("uploads", exist_ok=True)
        uploaded_file.save(save_path)

        # Append file info to message to send to model
        user_input += f"\n\n[User uploaded a file named '{filename}']"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost"
    }

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": user_input}
        ],
        "max_tokens": 150
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API request failed: {str(e)}"}), 500
    except (KeyError, IndexError):
        return jsonify({"error": "Unexpected API response format"}), 500

if __name__ == "__main__":
    app.run(debug=True)
