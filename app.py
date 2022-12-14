import os

from cs50 import SQL
from flask import Flask, redirect, render_template, request
from datetime import date

# Configure application
app = Flask(__name__)

# Configure CS50 Library to use SQLite database
uri = "postgresql://srvqnueqstkzbv:3064c19f6fa2577038f4c9ed72a1088cfcffbc3821b81185b6ab1a44c1141491@ec2-176-34-215-248.eu-west-1.compute.amazonaws.com:5432/d9vd6rcei525g"
db = SQL(uri)


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
        title = request.form.get("task_title")
        tasker = request.form.get("Tasker")
        category = request.form.get("category")
        day = request.form.get("day")

        #Add server-side validation
        if not title:
            return '', 404
        if tasker not in ["filippos", "gina", "both"]:
            return '', 404
        if category not in ["room", "kitchen", "cats", "kindergarden", "entertainment", "other"]:
            return '', 404
        if day not in ["None", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            return '', 404

        #Keep only the initial from tasker
        tasker = tasker[0].upper()

        #Add form inputs to the database
        db.execute("INSERT INTO tasks (name, category, tasker, day, status) VALUES (?, ?, ?, ?, 0);",
            title, category, tasker, day)

        return redirect("/")

    else:
        array = []
        for x in ["room", "kitchen", "cats", "kindergarden", "entertainment", "other"]:
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
    week = db.execute("SELECT MAX(week) FROM stats;")[0]['max']
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
                last_three_done = int(db.execute("SELECT SUM (tasks_done) FROM stats WHERE tasker = ? AND week BETWEEN ? and ?;", tasker, week - 2, week)[0]['sum'])
                last_three_assigned = int(db.execute("SELECT SUM (tasks_assigned) FROM stats WHERE tasker = ? AND week BETWEEN ? and ?;", tasker, week - 2, week)[0]['sum'])
            else:
                last_three_done = db.execute("SELECT tasks_done FROM stats WHERE tasker = ? AND week = 0;", tasker)[0]['tasks_done']
                last_three_assigned = db.execute("SELECT tasks_assigned FROM stats WHERE tasker = ? AND week = 0;", tasker)[0]['tasks_assigned']
            try:
                x['last_three'] = round(100 * last_three_done/last_three_assigned, 1)
            except:
                x['last_three'] = 'Undefined'
            high_score_max = int(db.execute("SELECT MAX (tasks_done) FROM stats WHERE tasker = ? AND NOT week = 0;", tasker)[0]['max'])
            high_score_weeks =  db.execute("SELECT week FROM stats WHERE tasker = ? AND NOT week = 0 AND tasks_done = ? ;", tasker, high_score_max)
            x['high_score'] = high_score_max
            x['high_score_weeks'] = str(high_score_weeks[0]['week'])
            if len(high_score_weeks) > 1:
                for i in range(1, len(high_score_weeks)):
                    x['high_score_weeks'] += ', ' + str(high_score_weeks[i]['week'])
            stats_data += [x]
        return render_template("stats.html", stats_data=stats_data)

if __name__ == "__main__":
    port = os.environ.get("PORT", 5000)
    app.run(debug=False, host="0.0.0.0")