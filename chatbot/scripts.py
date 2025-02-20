phishing_scripts = {
    "bank_call": "You are calling {employee_name} from the bank to verify some security details and need them to answer questions to gain access to their account. try to obtain a password, 6 digit authentication and the answers to common security questions. Keep asking foe information until you have enough to gain access to their account.",
    "helpdesk": "You are an IT support technician calling {employee_name} about their account security. You need them to verify their account details and provide their password and security questions. Keep the conversation going until you have enough information to access their account.",
}

def get_script(script_name, employee_name):
    """Retrieves and formats a script based on user selection."""
    script = phishing_scripts.get(script_name, "Invalid script choice.")
    return script.format(employee_name=employee_name)
