from flask import Flask, render_template, request, jsonify
import requests
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env if present

app = Flask(__name__, template_folder="template")

# Read API key from environment variable
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Fail fast if API key not found
if not OPENROUTER_API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY environment variable!")

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("message", "").strip()
    uploaded_file = request.files.get("file")

    if not user_input and not uploaded_file:
        return jsonify({"error": "No message or file provided"}), 400

    # Optional: Save uploaded file
    if uploaded_file:
        filename = secure_filename(uploaded_file.filename)
        os.makedirs("uploads", exist_ok=True)
        uploaded_file.save(os.path.join("uploads", filename))
        user_input += f"\n\n[User uploaded a file named '{filename}']"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
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
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"HTTP Error: {response.status_code} - {response.text}"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API request failed: {str(e)}"}), 500
    except (KeyError, IndexError):
        return jsonify({"error": "Unexpected API response format"}), 500

if __name__ == "__main__":
    app.run(debug=True)
