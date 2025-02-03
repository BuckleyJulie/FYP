from flask import Flask, render_template, request, session, jsonify
from chatbot.gpt import get_script_response
from chatbot.scripts import get_script

app = Flask(__name__)
app.secret_key = "super secret key"

@app.route("/", methods=["GET"])
def index():
    if "conversation" not in session:
        session["conversation"] = []
    return render_template("index.html", script=session["conversation"])

@app.route("/start", methods=["POST"])

def start_conversation():
    session["conversation"] = []
    session["script_initialized"] = False
    data = request.get_json()
    employee_name = data.get("employee_name")
    script_choice = data.get("script_choice")

    # Generate initial script
    initial_script = get_script(script_choice, employee_name)
    session["conversation"].append({"role": "assistant", "content": initial_script})
    session["script_initialized"] = True
    session.modified = True

    return jsonify({"conversation": session["conversation"]})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("user_input")

    if "conversation" not in session:
        session["conversation"] = []

    session["conversation"].append({"role": "user", "content": user_input})
    ai_response = get_script_response(user_input, session["conversation"])
    session["conversation"].append({"role": "assistant", "content": ai_response})
    session.modified = True

    return jsonify({"conversation": session["conversation"]})

if __name__ == "__main__":
    app.run(debug=True)
