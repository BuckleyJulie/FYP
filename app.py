from flask import Flask, render_template, request, session, jsonify, send_file, url_for
from chatbot.gpt import get_script_response
from chatbot.scripts import get_script
from chatbot.database import init_db, log_interaction, get_user_data
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os

app = Flask(__name__)
app.secret_key = "super secret key"

init_db()  # Ensure database is initialized

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

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
    report_url = url_for("generate_pdf_report", employee_name=employee_name, _external=True)

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

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        "Normal",
        parent=styles["Normal"],
        spaceAfter=5,
        leading=14,
    )
    elements = []

    elements.append(Paragraph(f"Security Awareness Training Report for {employee_name}", styles["Title"]))
    elements.append(Spacer(1, 12))
    
    table_data = [["Timestamp", "Script Type", "User Response", "AI Feedback"]]
    disclosed_info = set()
    training_recommendations = set()
    
    for entry in user_data:
        _, _, script, user_resp, ai_resp, timestamp = entry
        table_data.append([
            Paragraph(timestamp, normal_style),
            Paragraph(script, normal_style),
            Paragraph(user_resp, normal_style),
            Paragraph(ai_resp, normal_style)
        ])
        
        # Identifying disclosed information
        if "@" in user_resp:
            disclosed_info.add("Email Address")
            training_recommendations.add("Avoid Sharing Email Information with Unknown Sources")
        if "password" in user_resp.lower():
            disclosed_info.add("Password")
            training_recommendations.add("Never Share Passwords Over the Phone")
        if any(q in ai_resp.lower() for q in ["maiden name", "security question"]):
            disclosed_info.add("Security Answers")
            training_recommendations.add("Be Cautious When Answering Security Questions")
        if user_resp.isdigit() and len(user_resp) == 6:
            disclosed_info.add("Authentication Code")
            training_recommendations.add("Never Share Authentication Codes Over the Phone")
    
    table = Table(table_data, colWidths=[1.2 * inch, 1.2 * inch, 2.8 * inch, 2.8 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Disclosed Information:", styles["Heading2"]))
    elements.append(Spacer(1, 8))
    if disclosed_info:
        for info in disclosed_info:
            elements.append(Paragraph(f"- {info}", normal_style))
    else:
        elements.append(Paragraph("No sensitive information was disclosed.", normal_style))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Recommended Security Training Areas:", styles["Heading2"]))
    elements.append(Spacer(1, 8))
    if training_recommendations:
        for rec in training_recommendations:
            elements.append(Paragraph(f"- {rec}", normal_style))
    else:
        elements.append(Paragraph("No specific training recommendations needed.", normal_style))
    
    doc.build(elements)
    return send_file(pdf_path, as_attachment=True, mimetype='application/pdf')

if __name__ == "__main__":
    app.run(debug=True)
