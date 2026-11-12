from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///helpdesk.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Ticket model for the helpdesk system
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    issue = db.Column(db.String(100),nullable=False)
    description = db.Column(db.String(200),nullable=False)
    priority = db.Column(db.String(50),nullable=False)

with app.app_context():
    db.create_all()

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

    try:
        new_ticket = Ticket(name=name, issue=issue, description=description, priority=priority)
        db.session.add(new_ticket)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return "Error saving ticket"

    return render_template("submit.html",
                           name=name,
                           issue=issue,
                           description=description,
                           priority=priority)

@app.route("/tickets")
def tickets():
    tickets = Ticket.query.all()
    return render_template("tickets.html", tickets=tickets)