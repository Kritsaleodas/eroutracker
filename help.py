import os
from cs50 import SQL

uri = "postgresql://srvqnueqstkzbv:3064c19f6fa2577038f4c9ed72a1088cfcffbc3821b81185b6ab1a44c1141491@ec2-176-34-215-248.eu-west-1.compute.amazonaws.com:5432/d9vd6rcei525g"
db = SQL(uri)

last_three_done = int(db.execute("SELECT SUM (tasks_done) FROM stats WHERE tasker = 'F' AND week BETWEEN 3 and 5;")[0]['sum'])
print(last_three_done)