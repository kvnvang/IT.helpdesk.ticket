from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generalquestion")
def general_questions():
    return render_template("generalquestion.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form['name']
    issue = request.form['issue']
    description = request.form['description']
    priority = request.form['priority']

    return render_template("submit.html",
                           name=name,
                           issue=issue,
                           description=description,
                           priority=priority)
