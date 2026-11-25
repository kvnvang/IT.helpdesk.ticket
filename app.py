from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///helpdesk_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Ticket model for the helpdesk system # Week 11
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    issue = db.Column(db.String(100),nullable=False)
    description = db.Column(db.String(200),nullable=False)
    priority = db.Column(db.String(50),nullable=False)

    assignments = db.relationship('Assignment', backref='ticket', lazy=True, cascade='all, delete-orphan')

# Technician model for the helpdesk # WeeK 11
class Technician(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100))

    assignments = db.relationship('Assignment', backref='technician', lazy=True)

# Assignment model for the helpdesk
class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer,db.ForeignKey('ticket.id'), nullable=False)
    technician_id = db.Column(db.Integer,db.ForeignKey('technician.id'), nullable=False)

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

@app.route("/tickets/append_reminder", methods=["POST"])
def append_reminder():
    message_text = request.form.get('append-text', '').strip()
    priority_types = request.form.getlist('priority-selector')
    issue_type = request.form.get('issue-selector')
    tickets_to_update =[]
    

    if not message_text:
        error = "Please enter a reminder"
        tickets = Ticket.query.all()
        return render_template("tickets.html", tickets=tickets, error=error)

    try:
        if "all" in priority_types:
            tickets_to_update = Ticket.query.all()
        else:
            for priority_type in priority_types:
                for ticket in Ticket.query.filter_by(priority=priority_type).all():
                    tickets_to_update.append(ticket)

        for ticket in tickets_to_update:
            if issue_type == "all" or ticket.issue == issue_type:
                if message_text not in ticket.description:
                    ticket.description +=f" - {message_text}"
            db.session.add(ticket)
        db.session.commit()
        return redirect(url_for('tickets'))
    except Exception as e:
        db.session.rollback()
        error = f"Error updating tickets: {str(e)}"
        tickets = Ticket.query.all()
        return render_template("tickets.html", tickets=tickets, error=error)

@app.route("/tickets/delete_first")
def delete_first():
    try:
        all_tickets = Ticket.query.order_by(Ticket.id).all()

        if len(all_tickets) < 1:
            error = "You have no tickets to delete"
            tickets = Ticket.query.all()
            return render_template("tickets.html", tickets=tickets, error=error)

        first_ticket = all_tickets[0]
        db.session.delete(first_ticket)
        db.session.commit()
        return redirect(url_for('tickets'))

    except Exception as e:
        db.session.rollback()
        error = f"Error deleting ticket: {str(e)}"
        tickets = Ticket.query.all()
        return render_template("tickets.html", tickets=tickets, error=error)

@app.route("/tickets/delete_priority", methods=["POST"])
def delete_priority():
    priority_choice = request.form.getlist('priority-to-delete')

    try:
        if "all" in priority_choice:
            tickets_to_delete = Ticket.query.all()

            for ticket in tickets_to_delete:
                db.session.delete(ticket)

        else:
            for priority_type in priority_choice:
                tickets_to_delete = Ticket.query.filter_by(priority=priority_type).all()

                for ticket in tickets_to_delete:
                    db.session.delete(ticket)

        db.session.commit()
        return redirect(url_for("tickets"))

    except Exception as e:
        db.session.rollback()
        error = f"Error deleting tickets: {str(e)}"
        tickets = Ticket.query.all()
        return render_template("tickets.html", tickets=tickets, error=error)


@app.route("/tickets/deleteButton", methods=["POST"])
def delete_ticket():
    try:
        ticketId = request.form.get('ticketId', '').strip()
        ticket_to_delete = Ticket.query.filter_by(id=ticketId).first()

        if not ticket_to_delete:
            error = "No ticket found with the specified ID."
            tickets = Ticket.query.all()
            return render_template("tickets.html", tickets=tickets, error=error)

        db.session.delete(ticket_to_delete)
        db.session.commit()
        return redirect(url_for("tickets"))

    except Exception as e:
        db.session.rollback()
        error = f"Error deleting ticket: {str(e)}"
        tickets = Ticket.query.all()
        return render_template("tickets.html", tickets=tickets, error=error)

@app.route("/tickets/edit", methods=["GET", "POST"])
def edit_ticket():
    if request.method == "POST":
        ticketId = request.form.get("ticketId", '', type=int)

        if not ticketId:
            error = "No ticket id provided."
            tickets = Ticket.query.all()
            return render_template("tickets.html", tickets=tickets, error=error)

        ticketToUpdate = Ticket.query.filter_by(id=ticketId).first()

        if not ticketToUpdate:
            error = f"No ticket found with id {ticketId}."
            tickets = Ticket.query.all()
            return render_template("tickets.html", tickets=tickets, error=error)

        try:
            ticketToUpdate.name = request.form.get('name', ticketToUpdate.name)
            ticketToUpdate.issue = request.form.get('issue', ticketToUpdate.issue)
            ticketToUpdate.description = request.form.get('description', ticketToUpdate.description)
            ticketToUpdate.priority = request.form.get('priority', ticketToUpdate.priority)

            db.session.commit()
            return redirect(url_for("tickets"))

        except Exception as e:
            db.session.rollback()
            error = f"Error writing changes to database: {str(e)}"
            tickets = Ticket.query.all()
            return render_template("tickets.html", tickets=tickets, error=error)

    ticketId = request.args.get('ticketId')

    if not ticketId:
        error = "No ticket id provided."
        tickets = Ticket.query.all()
        return render_template("tickets.html", tickets=tickets, error=error)

    ticketToEdit = Ticket.query.filter_by(id=ticketId).first()

    if not ticketToEdit:
        error = f"No ticket found with id {ticketId}."
        tickets = Ticket.query.all()
        return render_template("tickets.html", tickets=tickets, error=error)

    return render_template("ticketEdit.html", ticket=ticketToEdit)
# Week 11 Route
@app.route('/technicians/add', methods=["GET", "POST"])
def add_technician():
    if request.method == 'POST':
        try:
            technician = Technician(
                name=request.form.get('name'),
                specialty=request.form.get('specialty')

            )

            db.session.add(technician)
            db.session.commit()
            return redirect(url_for('add_technician'))

        except Exception as e:
            db.session.rollback()
            error = f"Error addting technician: {e}"
            return render_template('add_technician.html', error=error)
    return render_template('add_technician.html')

# week 11 assignment route
@app.route('/assignments/add', methods=['GET', 'POST'])
def add_assignment():
    tickets = Ticket.query.all()
    technicians = Technician.query.all()

    if request.method == 'POST':
        try:
            assignment = Assignment(
                ticket_id=request.form.get('ticket_id'),
                technician_id=request.form.get('technician_id')
            )

            db.session.add(assignment)
            db.session.commit()

            return redirect(url_for('tickets'))

        except Exception as e:
            db.session.rollback()
            error = f"Error adding assignment: {e}"
            return render_template('add_assignment.html', tickets=tickets, technicians=technicians, error=error)

    return render_template('add_assignment.html', tickets=tickets, technicians=technicians)

# Week 11 Edit Assignment Route
@app.route('/assignments/edit/<int:id>', methods=['GET', 'POST'])
def edit_assignment(id):
    assignment = Assignment.query.get_or_404(id)
    tickets = Ticket.query.all()
    technicians = Technician.query.all()

    if request.method == 'POST':
        assignment.ticket_id = request.form.get('ticket_id')
        assignment.technician_id = request.form.get('technician_id')

        db.session.commit()

        return redirect(url_for('tickets'))

    return render_template('edit_assignment.html', assignment=assignment, tickets=tickets, technicians=technicians)

#  Week 11 Delete Assignment
@app.route('/assignments/delete/<int:id>')
def delete_assignment(id):
    assignment = Assignment.query.get_or_404(id)
    db.session.delete(assignment)
    db.session.commit()
    return redirect(url_for('tickets'))

# Week 11 All Technicians
@app.route('/technicians/view')
def view_by_technician():
    technicians = Technician.query.all()
    return render_template('display_by_technician.html', technicians=technicians)

# Week 11 View Individual Tech
@app.route('/technicians/view/<int:id>')
def view_technician(id):
    technician = Technician.query.get_or_404(id)
    return render_template('view_technician.html', technician=technician)