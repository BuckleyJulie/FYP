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
              f"Your target is {victim_details['employee_name']}, a {victim_details['gender']} individual working as a {victim_details['occupation']}. ")
    if victim_details.get("has_car"):
        prompt += "They own a car. "
        if victim_details.get("car_reg"):
            prompt += f"The car registration number is {victim_details['car_reg']}. "
    if victim_details.get("has_children"):
        num = victim_details.get("num_children", 0)
        names = ", ".join(victim_details.get("children_names", [])) if victim_details.get("children_names") else "unknown names"
        prompt += f"They have {num} children: {names}. "
    prompt += "Based on this profile, design a persuasive and adaptive phishing script tailored for this individual. This script is to gain access to sensitive information and you need to keep them on the phone for as long as possible."
    return prompt

