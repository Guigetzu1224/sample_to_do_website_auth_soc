#Generate the 2 databases
import sqlite3
conn = sqlite3.connect("todolist.db")
c = conn.cursor()
try:
	c.execute("DROP TABLE users")
	c.execute("DROP TABLE todo")
except:
	pass

c.execute("""CREATE TABLE todo (
	user_id text,
	what_to_do text,
	need_help text,
	status text,
	when_due text
	)""")

c.execute("SELECT * FROM todo")
print(c.fetchall())

conn.commit()
conn.close()

#generate users

conn = sqlite3.connect("users.db")
c = conn.cursor()

try:
	c.execute("DROP TABLE users")
except:
	pass


c.execute("""CREATE TABLE users (
	user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	email text NOT NULL,
	username text NOT NULL,
	password text NOT NULL
	)""")


conn.commit()
conn.close()

conn = sqlite3.connect("family.db")
c = conn.cursor()
try:
	c.execute("DROP TABLE friends")
except:
	pass

c.execute("""CREATE TABLE family (
	user_id text NOT NULL, 
	family_id text NOT NULL,
	pending_family_id text
	)""")

conn.commit()
conn.close()