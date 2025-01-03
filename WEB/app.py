from flask import Flask, request, jsonify, render_template, Response
import requests
import json

app = Flask(__name__)

RAG_SERVER_URL = "http://app:8001/stream"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/favicon.ico")
def favicon():
    return '', 204

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    history = request.json.get("history", [])[-3:]

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    payload = {"question": user_message, "history": history}
    headers = {"Content-Type": "application/json"}

    def generate():
        response = requests.post(RAG_SERVER_URL, json=payload, headers=headers, stream=True)
        if response.status_code != 200:
            yield f"Error: {response.status_code} - {response.text}"
            return

        for chunk in response.iter_lines(decode_unicode=False):
            if chunk.strip() == b"[DONE]":
                break
            if chunk.startswith(b"data: "):
                chunk = chunk[6:]
                try:
                    data = json.loads(chunk.decode("utf-8"))
                    content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue

    return Response(generate(), content_type="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
