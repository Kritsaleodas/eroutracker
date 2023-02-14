import os

from cs50 import SQL
from flask import Flask, redirect, render_template, request, Response
from datetime import date

# Configure application
app = Flask(__name__)

#Configure Database

#local-test database

#uri = "sqlite:///test.db"
# #project database
uri = "postgres://projectdatabase_user:sBW5Pe4KPe92aFWUvCXjkGJS8k5ZEcQ7@dpg-cflr94pgp3ju5h5smcvg-a/projectdatabase"
# uri = "sqlite:///project.db"
db = SQL(uri)

# max_week = 'MAX(week)'
# max_tasks_done = 'MAX(tasks_done)'
# sum_tasks_assigned = 'SUM(tasks_assigned)'
# sum_tasks_done = 'SUM(tasks_done)'

max_week = 'max'
max_tasks_done = 'max'
sum_tasks_assigned = 'sum'
sum_tasks_done = 'sum'

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        id = request.form['id']
        if request.form['where'] == 'delete':
            db.execute("DELETE FROM tasks WHERE name = ?", id)
            return '', 204
        elif request.form['where'] == 'Week':
            db.execute("UPDATE tasks SET status = 0 WHERE name = ?", id)
            return '', 204
        elif request.form['where'] == 'Today':
            db.execute("UPDATE tasks SET status = 1 WHERE name = ?", id)
            return '', 204
        elif request.form['where'] == 'Done':
            db.execute("UPDATE tasks SET status = 2 WHERE name = ?", id)
            db.execute("UPDATE tasks SET success = 1 WHERE name = ?", id)
            return '', 204
        elif request.form['where'] == 'fail':
            db.execute("UPDATE tasks SET status = 2, success = -1 WHERE name = ?", id)
            return '', 204
        elif request.form['where'] == 'unfail':
            db.execute("UPDATE tasks SET status = 2, success = 1 WHERE name = ?", id)
            return '', 204
    else:
        today = date.today().weekday()
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        db.execute("UPDATE tasks SET status = 1 WHERE day = ? AND status = 0;", days[today])
        return render_template("main.html")

@app.route("/week", methods=["GET", "POST"])
def week():
    if request.method == 'POST':
        return 404

    else:
        array = []
        for x in ["Room", "Kitchen", "Cats", "Kindergarden", "Entertainment", "Other"]:
            array += [db.execute("SELECT * FROM tasks WHERE category = ? AND status = 0;", x)]
        return render_template("week.html", array=array)

@app.route("/today")
def today():
    list = []
    for x in ["F", "G", "B"]:
        list += [db.execute("SELECT * FROM tasks WHERE tasker = ? AND status = 1;", x)]
    return render_template("today.html", list=list)

@app.route("/done")
def done():
    arrayz = []
    successful_tasks = []
    length = []
    for x in ["F", "G", "B"]:
        arrayz += [db.execute("SELECT * FROM tasks WHERE tasker = ? AND status = 2 ORDER BY success DESC, name ASC;", x)]
        successful_tasks += [len(db.execute("SELECT * FROM tasks WHERE tasker = ? AND status = 2 AND success = 1;", x))]
    for z in range(3):
        length += [len(arrayz[z])]
    return render_template("done.html", arrayz=arrayz, length=length, successful_tasks=successful_tasks)

@app.route("/stats", methods=["GET","POST"])
def stats():
    #week 0 is already added in the table so MAX(week) will always return an int (will never return NONE)
    week = db.execute("SELECT MAX(week) FROM stats;")[0][max_week]
    if request.method == 'POST':
        week += 1
        tasks_done = {}
        tasks_assigned = {}
        try:
            for tasker in ["F", "G", "B"]:
                tasks_done[tasker] = db.execute("SELECT COUNT (*) FROM tasks WHERE tasker = ? AND status = 2 AND success = 1;", tasker)[0]['COUNT (*)']
                tasks_assigned[tasker] = db.execute("SELECT COUNT (*) FROM tasks WHERE tasker = ? AND status = 2;", tasker)[0]['COUNT (*)']
                db.execute("INSERT INTO stats (week, tasker, tasks_done, tasks_assigned) VALUES (?, ?, ?, ?);",
                week, tasker, tasks_done[tasker], tasks_assigned[tasker])
                total_done = db.execute("SELECT tasks_done FROM stats WHERE week = 0 AND tasker = ?;", tasker)[0]['tasks_done'] + tasks_done[tasker]
                total_assigned = db.execute("SELECT tasks_assigned FROM stats WHERE week = 0 AND tasker = ?;", tasker)[0]['tasks_assigned'] + tasks_assigned[tasker]
                db.execute("UPDATE stats SET tasks_done = ? WHERE week = 0 AND tasker = ?;", total_done, tasker)
                db.execute("UPDATE stats SET tasks_assigned = ? WHERE week = 0 AND tasker = ?;", total_assigned, tasker)
                db.execute("DELETE FROM tasks;")
            return '', 204
        except:
            return '', 404
    else:
        if week == 0:
            return render_template("statsempty.html")
        else:
            stats_data = []
            for tasker in ["F", "G", "B"]:
                x = {}
                x['total_tasks_done'] = db.execute("SELECT tasks_done FROM stats WHERE week = 0 AND tasker = ?;", tasker)[0]['tasks_done']
                x['total_tasks_assigned'] = db.execute("SELECT tasks_assigned FROM stats WHERE week = 0 AND tasker = ?;", tasker)[0]['tasks_assigned']
                try:
                    x['success_ratio'] = round(100 * x['total_tasks_done']/x['total_tasks_assigned'], 1)
                except:
                    x['success_ratio'] = 'Undefined'
                if week >= 3:
                    last_three_done = int(db.execute("SELECT SUM(tasks_done) FROM stats WHERE tasker = ? AND week BETWEEN ? and ?;", tasker, week - 2, week)[0][sum_tasks_done])
                    last_three_assigned = int(db.execute("SELECT SUM(tasks_assigned) FROM stats WHERE tasker = ? AND week BETWEEN ? and ?;", tasker, week - 2, week)[0][sum_tasks_assigned])
                else:
                    last_three_done = db.execute("SELECT tasks_done FROM stats WHERE tasker = ? AND week = 0;", tasker)[0]['tasks_done']
                    last_three_assigned = db.execute("SELECT tasks_assigned FROM stats WHERE tasker = ? AND week = 0;", tasker)[0]['tasks_assigned']
                try:
                    x['last_three'] = round(100 * last_three_done/last_three_assigned, 1)
                except:
                    x['last_three'] = 'Undefined'
                high_score_max = int(db.execute("SELECT MAX(tasks_done) FROM stats WHERE tasker = ? AND NOT week = 0;", tasker)[0][max_tasks_done])
                high_score_weeks =  db.execute("SELECT week FROM stats WHERE tasker = ? AND NOT week = 0 AND tasks_done = ? ;", tasker, high_score_max)
                x['high_score'] = high_score_max
                x['high_score_weeks'] = str(high_score_weeks[0]['week'])
                if len(high_score_weeks) > 1:
                    for i in range(1, len(high_score_weeks)):
                        x['high_score_weeks'] += ', ' + str(high_score_weeks[i]['week'])
                stats_data += [x]
            return render_template("stats.html", stats_data=stats_data)

@app.route("/add_task", methods=["POST"])
#This handles the request of adding a task `
def add_task():
    #Get input fields from the form
    title = request.form.get("task_title")
    tasker = request.form.get("Tasker")
    category = request.form.get("category")
    day = request.form.get("day")

    #Server-side validation
    if not title:
        return '', 404
    if tasker not in ["Filippos", "Gina", "Both"]:
        return '', 404
    if category not in ["Room", "Kitchen", "Cats", "Kindergarden", "Entertainment", "Other"]:
        return '', 404
    if day not in ["None", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        return '', 404

    #Keep only the initial from tasker
    tasker = tasker[0]

    #Insert form inputs to the database with status as 0
    db.execute("INSERT INTO tasks (name, category, tasker, day, status) VALUES (?, ?, ?, ?, 0);",
        title, category, tasker, day)

    return redirect("/")

@app.route("/delete_task", methods=["POST"])
def delete_task():
    name = request.form['task_name']
    current_page = request.form['current_page']
    try:
        db.execute("DELETE FROM tasks WHERE name = ?", name)
        return redirect(current_page)
    except:
        return Response(status=404)



@app.route("/one_time_action")
def one_time_action():
    #I will be using this to perform actions that only need to be carried out once, e.g. clear the database or stats table
    db.execute("CREATE TABLE tasks (name TEXT PRIMARY KEY, category TEXT NOT NULL, day TEXT, tasker TEXT NOT NULL, status INTEGER NOT NULL, success INTEGER);")
    db.execute("CREATE TABLE stats (week INTEGER NOT NULL, tasker TEXT NOT NULL, tasks_done INTEGER, tasks_assigned INTEGER);")
    for tasker in ["G", "F", "B"]:
      db.execute("INSERT INTO stats (week, tasker, tasks_done, tasks_assigned) VALUES (0, ?, 0, 0)", tasker)
    return redirect("/")

if __name__ == "__main__":
    port = os.environ.get("PORT", 5000)
    app.run(debug=False, host="0.0.0.0")