# 🎓 Final Year Project – AI Phishing Script Simulator

**Julie Buckley**  
Student No: **C00200976**  
South East Technological University, Carlow  
**Supervisor:** Dr. Christopher Staff

---

## 📄 Project Overview

This project simulates AI-aided phishing conversations using both **voice input (transcribed locally)** and **live GPT-4 Turbo responses from OpenAI**. It demonstrates how generative AI can be used to craft socially engineered attacks in a realistic and interactive environment — highlighting the potential risks posed by AI-driven phishing techniques.

---

## 🚀 Features

- 🎤 **Voice-to-text phishing** using OpenAI Whisper (runs locally)
- 💬 **GPT-4 Turbo-generated phishing responses** (via OpenAI API)
- 🧠 Custom scenarios based on victim’s job, location, and company
- 📦 Automatically logs interactions and generates downloadable reports
- 🧪 Ideal for cybersecurity training, awareness, or academic demo purposes

---

## ⚙️ Tech Stack

- Python 3.10
- Flask
- OpenAI Whisper (local)
- PyTorch (Metal-accelerated on Apple M1 Pro)
- HTML/CSS + Vanilla JS
- SQLite (for interaction logging)

---

## 🛠️ Getting Started

### 1. Clone the repository

git clone https://github.com/BuckleyJulie/FYP.git
cd FYP
### 2. Create a virtual environment

pyenv virtualenv 3.10.13 whisper310
pyenv activate whisper310

### OR using standard venv

python3.10 -m venv whisper-env
source whisper-env/bin/activate

### 3. Install dependancies

pip install -r requirements.txt

### 4. Create a `.env` file for your OpenAI API key

In the project root, create a `.env` file with the following:
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
> 🔒 **Keep this key secret** and never commit it to version control. Your `.gitignore` should already exclude `.env`.

### 5. Run the app

python app.py

### 6. Open the app in the browser

http://127.0.0.1:5000


---
## 💡 Notes

- Whisper runs locally and does not require an API key.
- **Text-based AI responses are powered by OpenAI GPT-4 Turbo**, which requires an API key (`OPENAI_API_KEY`).
- Transcription and response are both tailored to live user input.
- Tested on macOS with M1 Pro using Metal-accelerated PyTorch.


---

### 🧪 Example Use Cases

✅ Cybersecurity awareness training

✅ Simulating phishing attacks in academic environments

✅ Testing human response to AI-generated manipulation

--- 
### 📧 Contact

For academic or demonstration use only.

📩 julieb@live.ie

🔗 https://github.com/BuckleyJulie/FYP





