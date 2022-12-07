
from cs50 import SQL

db = SQL("sqlite:///project.db")

db.execute("DELETE FROM stats WHERE NOT week = 0;")
x = db.execute("UPDATE stats SET tasks_done = 0, tasks_assigned = 0 WHERE week = 0;")

