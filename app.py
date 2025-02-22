from flask import Flask, render_template, request, session, jsonify, send_file
from chatbot.gpt import get_script_response
from chatbot.scripts import get_script
from chatbot.database import init_db, log_interaction, get_user_data
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

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
    report_url = f"/report/{employee_name}.pdf"

    # Clear the session
    session.pop("conversation", None)
    session.pop("script_initialized", None)
    session.pop("employee_name", None)
    session.pop("script_type", None)

    return jsonify({"message": "Chat ended. Report generated.", "report_url": report_url})

@app.route("/report/<employee_name>.pdf", methods=["GET"])
def generate_pdf_report(employee_name):
    user_data = get_user_data(employee_name)
    pdf_path = f"reports/{employee_name}_report.pdf"

    if not user_data:
        return jsonify({"error": "No data found for this employee."}), 404

    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, f"Security Awareness Training Report for {employee_name}")
    c.line(50, height - 55, 550, height - 55)
    
    y_position = height - 80
    c.setFont("Helvetica", 10)

    for entry in user_data:
        _, _, script, user_resp, ai_resp, timestamp = entry
        c.drawString(50, y_position, f"Timestamp: {timestamp}")
        y_position -= 15
        c.drawString(50, y_position, f"Script Type: {script}")
        y_position -= 15
        c.drawString(50, y_position, f"User Response: {user_resp}")
        y_position -= 15
        c.drawString(50, y_position, f"AI Feedback: {ai_resp}")
        y_position -= 25
        if y_position < 100:
            c.showPage()
            y_position = height - 50
    
    c.save()
    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
