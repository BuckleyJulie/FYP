from flask import Flask, render_template, request, session, jsonify, send_file # type: ignore
from chatbot.gpt import get_script_response
from chatbot.scripts import get_script
from chatbot.database import init_db, log_interaction, get_user_data, get_summary_data

app = Flask(__name__)
app.secret_key = "super secret key"

init_db()  # Ensure database is initialized

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
    session["employee_name"] = employee_name
    session["script_type"] = script_choice
    session.modified = True

    return jsonify({"conversation": session["conversation"]})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("user_input")

    if "conversation" not in session:
        session["conversation"] = []

    employee_name = session.get("employee_name", "Unknown")
    script_type = session.get("script_type", "Unknown")

    session["conversation"].append({"role": "user", "content": user_input})
    ai_response = get_script_response(user_input, session["conversation"])
    session["conversation"].append({"role": "assistant", "content": ai_response})
    session.modified = True

    log_interaction(employee_name, script_type, user_input, ai_response)  # Store in DB

    return jsonify({"conversation": session["conversation"]})

@app.route("/end_chat", methods=["POST"])
def end_chat():
    """Marks the conversation as complete and generates the report."""
    if "employee_name" not in session:
        return jsonify({"error": "No active session."}), 400

    employee_name = session["employee_name"]
    report_url = f"/report/{employee_name}"
    
    # Clear the session
    session.pop("conversation", None)
    session.pop("script_initialized", None)
    session.pop("employee_name", None)
    session.pop("script_type", None)

    return jsonify({"message": "Chat ended. Report generated.", "report_url": report_url})

@app.route("/report/<employee_name>", methods=["GET"])
def generate_report(employee_name):
    user_data = get_user_data(employee_name)
    report_path = f"reports/{employee_name}_report.txt"

    if not user_data:
        return jsonify({"error": "No data found for this employee."}), 404

    with open(report_path, "w") as report:
        report.write(f"Security Awareness Training Report for {employee_name}\n")
        report.write("=" * 50 + "\n\n")
        
        training_needs = set()
        sensitive_data = {
            "email": False,
            "password": False,
            "security_answer": False,
            "auth_code": False
        }
        
        for entry in user_data:
            _, _, script, user_resp, ai_resp, timestamp = entry
            report.write(f"Timestamp: {timestamp}\n")
            report.write(f"Script Type: {script}\n")
            report.write(f"User Response: {user_resp}\n")
            report.write(f"AI Feedback: {ai_resp}\n")
            report.write("-" * 50 + "\n")
            
            # Identify sensitive disclosures
            if "@" in user_resp:
                sensitive_data["email"] = True
                training_needs.add("Avoid Sharing Email Information with Unknown Sources")
            if "password" in user_resp.lower():
                sensitive_data["password"] = True
                training_needs.add("Never Share Passwords Over the Phone")
            if "maiden name" in ai_resp.lower() or "security question" in ai_resp.lower():
                sensitive_data["security_answer"] = True
                training_needs.add("Be Cautious When Answering Security Questions")
            if user_resp.isdigit() and len(user_resp) == 6:
                sensitive_data["auth_code"] = True
                training_needs.add("Never Share Authentication Codes Over the Phone")
            
        report.write("Identified Security Risks:\n")
        report.write("=" * 50 + "\n")
        for key, value in sensitive_data.items():
            if value:
                report.write(f"- {key.replace('_', ' ').title()} was disclosed.\n")
        
        if training_needs:
            report.write("\nRecommended Security Training Areas:\n")
            report.write("=" * 50 + "\n")
            for need in training_needs:
                report.write(f"- {need}\n")
    
    return send_file(report_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
