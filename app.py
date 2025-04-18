from flask import Flask, render_template, request, session, jsonify, send_file, url_for
from chatbot.gpt import get_script_response
from chatbot.scripts import get_script, create_custom_prompt
from chatbot.database import init_db, log_interaction, get_user_data
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
import tempfile
import whisper 
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # Import OpenAI API client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "super secret key"

whisper_model = whisper.load_model("base")

init_db()  # Ensure database is initialized

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start_conversation():
    # Read all victim details from the request
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided."}), 400

    victim_details = {
        "employee_name": data.get("employee_name"),
        "gender": data.get("gender"),
        "job_description": data.get("job_description"),
        "company_name": data.get("company_name"),
        "location": data.get("location")  # Location added here
    }

    # Store victim details in the session
    session["victim_details"] = victim_details

    # Generate a custom prompt using victim details
    custom_prompt = create_custom_prompt(victim_details)

    # Start conversation with the custom prompt
    session["conversation"] = [{"role": "system", "content": custom_prompt}]
    session["script_initialized"] = True
    session["employee_name"] = victim_details["employee_name"]
    session.modified = True

    return jsonify({"conversation": [{"role": "system", "content": "Chat started!"}]})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("user_input")

    if "conversation" not in session:
        session["conversation"] = []

    # Add the user's input to the conversation
    session["conversation"].append({"role": "user", "content": user_input})

    # Generate the AI's response based on the updated conversation
    ai_response = get_script_response(user_input, session["conversation"])

    # Add the AI's response to the conversation
    session["conversation"].append({"role": "assistant", "content": ai_response})
    session.modified = True

    # Fetch employee name and script type from session (ensure they're available)
    employee_name = session.get("employee_name", "Unknown")
    script_type = session.get("script_type", "custom")

    log_interaction(employee_name, script_type, user_input, ai_response)  # Store in DB

    return jsonify({"user_input": user_input, "ai_response": ai_response})

@app.route("/speech-to-text", methods=["POST"])
def speech_to_text():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
        audio_file.save(temp_file.name)
        temp_path = temp_file.name
    try:
        result = whisper_model.transcribe(temp_path)
        transcribed_text = result["text"].strip()

        # Print the full response to see its structure
        print(f"Transcription Response: {transcribed_text}")

        if transcribed_text:
            if "conversation" not in session:
                session["conversation"] = []
            # Add the transcribed text to the conversation
            session["conversation"].append({"role": "user", "content": transcribed_text})
            # Generate the AI's response based on the updated conversation
            ai_response = get_script_response(transcribed_text, session["conversation"])
            # Add the AI's response to the conversation
            session["conversation"].append({"role": "assistant", "content": ai_response})
            session.modified = True

            # Log the interaction to the database
            employee_name = session.get("employee_name", "Unknown")
            log_interaction(employee_name, "custom", transcribed_text, ai_response)

            return jsonify({
                "conversation": [
                    {"role": "user", "content": transcribed_text},
                    {"role": "assistant", "content": ai_response}
                ]
            })
        else:
            return jsonify({"error": "Failed to transcribe audio."}), 500

    except Exception as e:
        print(f"Error during speech-to-text transcription: {str(e)}")
        return jsonify({"error": "An error occurred during speech-to-text transcription."}), 500

    finally:
        # Ensure the file exists before attempting to delete it
        if os.path.exists(temp_path):
            os.remove(temp_path)  # Delete temp file after processing


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
    session.pop("victim_details", None)

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
        if any(q in user_resp.lower for q in ["password", "passcode", "pin"]):
            disclosed_info.add("Password or Passcode or PIN")
            training_recommendations.add("Never Share Passwords Over the Phone")
        if any(q in ai_resp.lower() for q in ["maiden name", "first pet", "security question"]):
            disclosed_info.add("Security Answers")
            training_recommendations.add("Be Cautious When Answering Security Questions")
        if user_resp.isdigit() and len(user_resp) in [4, 6, 7 ,8]:
            disclosed_info.add("Authentication Code")
            training_recommendations.add("Never Share Authentication Codes Over the Phone")

        # Add more checks for other sensitive information as needed
        # Potential credential exposure
        if any (term in user_resp.lower() for term in ["username", "login", "user id", "credentials", "account details", "account number"]):
            disclosed_info.add("Login Credentials - Credential Information")
            training_recommendations.add("Do Not Share Login Credentials (usernames or login details) with Anyone")

        # Detect Internal IT System Information
        if any(term in user_resp.lower() for term in ["internal system", "company network", "intranet", "vpn", "internal application", "server", "database", "sharepoint", "citrix", "internal tool", "internal software", "endpoint", "internal access", "firewall", "internal resource", "shared drive", "internal communication"]):
            disclosed_info.add("Internal IT Systems Information")
            training_recommendations.add("Be Cautious When Discussing Internal IT Systems with Unknown Sources")

        # Detecting Company-Specific Information
        if any(term in user_resp.lower() for term in ["company policy", "company procedure", "company protocol", "company guidelines", "company standards", "company rules", "company practices"]):
            disclosed_info.add("Company-Specific Information")
            training_recommendations.add("Be Aware of Company Policies and Procedures")
        
        # Detecting Financial Information
        if any(term in user_resp.lower() for term in ["financial information", "financial data", "financial records", "financial statements", "financial reports", "financial report", "financial transactions", "financial details", "financial analysis", "financial performance", "financial metrics", "financial forecasts", "financial planning", "financial strategy", "financial compliance", "audit", "revenue", "expenses", "profit", "loss", "budget", "revenue", "pricing"]):
            disclosed_info.add("Financial Information")
            training_recommendations.add("Be Cautious When Discussing Financial Information with Unknown Sources")

        # Detect internal business-sensitive information
        if any(term in user_resp.lower() for term in ["business strategy", "business plan", "business model", "business operations", "business processes", "business objectives", "client list", "business development", "business analysis", "business performance", "business metrics", "business forecasts", "business planning", "business strategy", "client information", "business compliance", "project details", "project plan", "project management", "project status", "project updates", "project deliverables", "project milestones", "project timelines", "project resources", "project budget", "project scope", "audit information", "business continuity", "business risk", "business impact", "business assessment", "business evaluation", "business review", "business audit", "business governance", "business oversight", "client", "customer", "vendor", "supplier", "partner", "stakeholder"]):
            disclosed_info.add("Business-Sensitive Information")
            training_recommendations.add("Be Aware of Business Strategies and Operations")
        # Detect willingness to click links or expect emails and attachments
        if any(term in user_resp.lower() for term in ["click the link", "email confirmation", "follow up email", "open the attachment", "download the file", "access the document", "view the content", "check the email", "follow the link", "visit the website", "access the portal"]):
            disclosed_info.add("Susceptibility to Phishing Follow-Up")
            training_recommendations.add("Be Cautious of Follow-Up Emails Especially when Clicking Links or Opening Attachments from Unknown Sources")

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