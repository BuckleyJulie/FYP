from flask import Flask, render_template, request
from chatbot.gpt import get_script_response
from chatbot.scripts import get_script

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        employee_name = request.form["employee_name"]
        script_choice = request.form["script_choice"]
        initial_script = get_script(script_choice, employee_name)
        return render_template("index.html", script=initial_script)

    return render_template("index.html", script=None)

if __name__ == "__main__":
    app.run(debug=True)
