from flask import Flask, request, jsonify, render_template
from agent import create_agent

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    message = request.form.get("message") or request.json.get("message")
    if not message:
        return jsonify({"error": "No message provided"}), 400
    # Create a fresh agent and tool-server context per request
    agent = create_agent()
    with agent:
        answer = agent.ask(message)
    return jsonify({"response": answer})

if __name__ == "__main__":
    app.run(debug=True)