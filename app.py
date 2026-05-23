from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta, timezone
from flask_sqlalchemy import SQLAlchemy
import os
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.permanent_session_lifetime = timedelta(weeks = 999)

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    priority = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.String(50), nullable = False)
with app.app_context():
    db.create_all()

def calculate_priority(date):
    IST = timezone(timedelta(hours=5, minutes=30))
    CEST = timezone(timedelta(hours = 8, minutes = 0))
    due_date = datetime.strptime(date, '%Y-%m-%d')
    current_date = datetime.now(IST).date()
    if due_date.date() < current_date.date() or due_date.date() == current_date.date() - timedelta(days=1):
        priority = "Date Missed"
    elif due_date.date() == current_date.date():
        priority = "Very High"
    elif current_date + timedelta(days=3) >= due_date > current_date:
        priority = "High"
    elif current_date + timedelta(days=7) >= due_date > current_date + timedelta(days=3):
        priority = "Medium"
    else:
        priority = "Low"
    return priority

i = 0
@app.route('/', methods=['POST', 'GET'])
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if 'user_id' in session:
            return redirect(url_for('your_tasks'))
        else:
            session.permanent = True
            user = request.form['user_id']
            session['user_id'] = user
            return redirect(url_for('your_tasks'))
    return render_template("login.html")

@app.route('/add-task', methods=['POST', 'GET'])
def add_tasks():
    global i
    if request.method == 'POST':
        user_id = session['user_id']
        title = request.form['ts']
        date = request.form['dt']
        description = request.form.get('ds')
        task = Tasks(title = title, date = date, description = description, priority = calculate_priority(date), user_id = user_id)
        db.session.add(task)
        db.session.commit()
        i += 1
        return redirect(url_for('your_tasks'))       
    return render_template("add_task.html")

@app.route('/your-tasks', methods = ['GET', 'POST'])
def your_tasks():
    tasks = db.session.execute(db.select(Tasks).filter_by(user_id=session['user_id'])).scalars().all()
    if request.method == 'POST':
        for task in tasks:
            task.priority = calculate_priority(task.date)
    return render_template("your_tasks.html", tasks=tasks)

@app.route('/delete-task', methods=['POST', 'GET'])
def delete_task():
    task_id = request.args.get('task_id')
    tasks = db.session.get(Tasks, int(task_id))
    if tasks:
        db.session.delete(tasks)
        db.session.commit()

    return redirect(url_for('your_tasks'))

if __name__ == "__main__":
    app.run(host = '0.0.0.0', debug=True)
