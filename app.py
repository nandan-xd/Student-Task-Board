from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.permanent_session_lifetime = timedelta(weeks = 999)
i=0
@app.route('/', methods=['POST', 'GET'])
@app.route('/add-task', methods=['POST', 'GET'])
def add_tasks():
    global i
    priority = ''
    for j in range(1):
        if request.method == 'POST':
            title = request.form['ts']
            date = request.form['dt']
            description = request.form.get('ds')
            task = session.get('task', [])
            due_date = datetime.strptime(date, '%Y-%m-%d')
            current_date = datetime.now()
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
            task.append({'title': title, 'date': date, 'description': description or "No description provided", 'id': i, 'priority': priority})
            session['task'] = task
            i += 1
            return redirect(url_for('your_tasks'))
        
    return render_template("add_task.html")

@app.route('/your-tasks', methods = ['GET', 'POST'])
def your_tasks():
    tasks = session.get('task', [])
    if request.method == 'POST':
        for task in tasks:
            date = request.form['dt']
            due_date = datetime.strptime(date, '%Y-%m-%d')
            current_date = datetime.now()
            if due_date.date() < current_date.date() or due_date.date() == current_date.date() - timedelta(days=1):
                task['priority'] = "Date Missed"
            elif due_date.date() == current_date.date():
                task['priority'] = "Very High"
            elif current_date + timedelta(days=3) >= due_date > current_date:
                task['priority'] = "High"
            elif current_date + timedelta(days=7) >= due_date > current_date + timedelta(days=3):
                task['priority'] = "Medium"
            else:
                task['priority'] = "Low"
        session['tasks'] = tasks
    return render_template("your_tasks.html", tasks=tasks)

@app.route('/delete-task', methods=['POST', 'GET'])
def delete_task():
    task_id = request.args.get('task_id')
    tasks = session.get('task', [])
    for j in range(len(tasks)):
        if tasks[j]['id'] == int(task_id):
            del tasks[j]
            break
        elif len(tasks) == 0:
            tasks.clear()
            break
            
    session['task'] = tasks

    return redirect(url_for('your_tasks'))

if __name__ == "__main__":
    app.run(debug=True)