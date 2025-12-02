from flask import Flask, request, jsonify
from flask_cors import CORS
import os, requests, json, re
from dotenv import load_dotenv
from pipelines.youtube_fetcher import fetch_comments

# ----- Load environment variables -----
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")

# ----- Initialize Flask -----
app = Flask(__name__)
CORS(app)  # enable CORS for extension/frontend


# ======================================================
#  GEMINI CALL
# ======================================================
def call_gemini(prompt_text):
    url = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt_text}]
            }
        ]
    }

    try:
        response = requests.post(url, json=payload)

        if not response.ok:
            return f"❌ Gemini Error {response.status_code}: {response.text}"

        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return f"❌ Exception: {str(e)}"



# ======================================================
#  SUMMARIZE COMMENTS
# ======================================================
def summarize_comments(video_id):
    comments = fetch_comments(video_id)
    if not comments or ("❌" in comments[0]):
        return comments

    prompt = f"Summarize the following YouTube comments concisely:\n\n{chr(10).join(comments)}"
    summary = call_gemini(prompt)
    return [summary]



# ======================================================
#  ANALYZE SENTIMENT
# ======================================================
def analyze_sentiment(video_id):
    comments = fetch_comments(video_id)
    if not comments or ("❌" in comments[0]):
        return comments

    prompt = f"Analyze the sentiment (positive/neutral/negative) of these YouTube comments:\n\n{chr(10).join(comments)}"
    sentiment_result = call_gemini(prompt)
    return [sentiment_result]



# ======================================================
#  ROUTES
# ======================================================

@app.route("/", methods=["GET"])
def home():
    return "✅ AI Assistant backend running!"


@app.route("/command", methods=["POST"])
def command():
    data = request.json
    user_command = data.get("command", "")

    # ---- Try direct JSON ----
    try:
        command_json = json.loads(user_command)
    except:
        # ---- Ask Gemini to convert command → JSON ----
        prompt = f"""
Convert this instruction into a JSON command with keys "action" and optional "video_id".

Example:
Input: "Fetch comments for video abc123"
Output: {{ "action": "fetch_comments", "video_id": "abc123" }}

Now process: "{user_command}"
"""

        url = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={API_KEY}"
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        try:
            response = requests.post(url, json=payload)
            result = response.json()

            # Extract text response
            reply = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")

            # Remove ```json code blocks
            cleaned_reply = re.sub(r"```(?:json)?\n(.*?)\n```", r"\1", reply, flags=re.DOTALL)

            command_json = json.loads(cleaned_reply)

        except Exception as e:
            return jsonify({"error": f"Gemini API request failed: {str(e)}"})

    # ---- Extract action ----
    action = command_json.get("action")
    video_id = command_json.get("video_id")

    # ---- Route to correct feature ----
    if action == "fetch_comments":
        return jsonify({"result": fetch_comments(video_id)})

    elif action == "summarize_comments":
        return jsonify({"result": summarize_comments(video_id)})

    elif action == "analyze_sentiment":
        return jsonify({"result": analyze_sentiment(video_id)})

    # Unknown action
    return jsonify({"error": "Unknown action", "parsed": command_json})



# ======================================================
#  MAIN (for local testing)
# ======================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
