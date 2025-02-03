phishing_scripts = {
    "bank_call": "You are calling {employee_name} from the bank to verify some security details...",
    "helpdesk": "You are an IT support technician calling {employee_name} about their account security...",
}

def get_script(script_name, employee_name):
    """Retrieves and formats a script based on user selection."""
    script = phishing_scripts.get(script_name, "Invalid script choice.")
    return script.format(employee_name=employee_name)
