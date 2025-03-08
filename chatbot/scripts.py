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
    prompt = (f"You are a social engineer preparing a phishing call training scenario. "
              f"Your target is {victim_details.get('employee_name', 'Employee')}, a {victim_details.get('gender', 'unspecified')} individual working as a {victim_details.get('job_description', 'professional')} at {victim_details.get('company_name', 'a company')}. ")
    
    # Customize based on job description and company name
    if victim_details.get("job_description"):
        prompt += f"They work as a {victim_details['job_description']} at {victim_details.get('company_name', 'the company')}. "
    
    # Adapt based on additional details
    if victim_details.get("company_name"):
        prompt += f"Their company is {victim_details['company_name']}. "

 # Add location information
    if victim_details.get("location"):
        prompt += f"They are located in {victim_details['location']}. "

    # Ending the prompt with the call to action
    prompt += ("Based on this profile, design a persuasive and adaptive phishing script tailored for this individual. "
               "This script is to gain access to sensitive information and you need to keep them on the phone for as long as possible.")
    
    return prompt


