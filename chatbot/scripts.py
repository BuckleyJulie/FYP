# chatbot/scripts.py

def get_script(script_choice, victim_name):
    """
    Returns an initial phishing script based on the chosen scenario.
    """
    if script_choice == "bank_call":
        return f"You are calling {victim_name} from the bank to verify some account details. Be persuasive but cautious."
    elif script_choice == "helpdesk":
        return f"You are calling {victim_name} from IT support to address security concerns regarding their account."
    else:
        return "Default phishing script."

def create_custom_prompt(victim_details):
    """
    Constructs a custom prompt for the AI based on detailed victim information.
    """
    prompt = (
        f"You are a skilled social engineer conducting a simulated phishing call for cybersecurity training purposes. "
        f"The target is {victim_details['employee_name']}, who identifies as {victim_details['gender']} and currently works as {victim_details['job_description']} "
        f"at {victim_details['company_name']} located in {victim_details['location']}.\n\n"
        
        "Step 1: Evaluate the provided job description and company details carefully. Identify types of sensitive information "
        "this employee is likely to access (e.g., financial details, intellectual property, customer data, login credentials, internal communications, confidential processes).\n\n"
        
        "Step 2: Based on this evaluation, craft a persuasive and adaptive social engineering script designed to convincingly impersonate a trusted individual "
        "or authority relevant to their role or company. The script's primary goal is to subtly and effectively extract as much sensitive information as possible, "
        "which could potentially be exploited in a real-world cyber attack scenario.\n\n"
        
        "Step 3: Begin the interaction naturally, aiming to establish trust and maintain the employee's engagement. Adapt your approach dynamically based on their responses, "
        "leveraging any volunteered information to deepen trust and progressively request increasingly sensitive details.\n\n"
        
        "Ensure the interaction remains professional and believable, reflecting realistic methods used in actual social engineering attacks. "
        "The outcome of this scenario will be recorded and used by HR to assess the employee's awareness and determine necessary cybersecurity training."
    )
    return prompt


