from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.permanent_session_lifetime = timedelta(weeks = 999)
task = []
@app.route('/', methods=['POST', 'GET'])
@app.route('/add-task', methods=['POST', 'GET'])
def add_tasks():
    priority = ""
    for i in range(1):
        if request.method == 'POST':
            title = request.form['ts']
            date = request.form['dt']
            description = request.form.get('ds')
            due_date = datetime.strptime(date, '%Y-%m-%d')
            current_date = datetime.now()
            if due_date < current_date:
                priority = "Date Missed"
            elif due_date == current_date:
                priority = "Very High"
            elif current_date + timedelta(days=3) >= due_date > current_date:
                priority = "High"
            elif current_date + timedelta(days=7) >= due_date > current_date + timedelta(days=3):
                priority = "Medium"
            else:
                priority = "Low"
            task.append({'title': title, 'date': date, 'description': description or "No description provided", 'priority': priority})
            session['task'] = task
            #print(task)
            # return redirect(url_for('your_tasks'))
        
    return render_template("add_task.html")

@app.route('/your-tasks')
def your_tasks():
    tasks = session.get('task', [])
    return render_template("your_tasks.html", tasks=tasks)

@app.route('/delete-task', methods=['POST'])
def delete_task():
    tasks = session.get('task', [])
    if tasks:
        delete = tasks.pop()
        session['task'] = tasks 
    return redirect(url_for('your_tasks', delete=delete))

if __name__ == "__main__":
    app.run(debug=True)