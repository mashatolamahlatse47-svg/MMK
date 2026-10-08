from flask import Flask, request, jsonify

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "MMK Studio AI"
    })

@app.post("/api/ai/hook")
def generate_hook():
    data = request.get_json(silent=True) or {}
    idea = str(data.get("idea", "")).strip()

    if not idea:
        return jsonify({"error": "Please provide a song idea."}), 400

    return jsonify({
        "status": "ready",
        "message": "AI Hook Engine endpoint is ready.",
        "idea": idea
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8091, debug=False)
