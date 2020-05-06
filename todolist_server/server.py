# This is a simple example web app that is meant to illustrate the basics.
from flask import Flask, render_template, redirect, g, request, url_for, jsonify
import sqlite3
import json

DATABASE = 'todolist.db'
app = Flask(__name__)
app.config.from_object(__name__)

'''
user_id INTEGER,
	what_to_do text,
	need_help BOOLEAN,
	status BOOLEAN,
	when_due text
'''
@app.route("/api/items",methods=['GET'])
def get_items():
	with sqlite3.connect(DATABASE) as connection:
		db = connection.cursor()
		DATA = request.json
		DATA = json.loads(DATA)
		user_id = DATA['user_id']
		cur = db.execute('SELECT what_to_do, when_due, need_help, status, user_id FROM todo WHERE user_id="'+user_id+'"')
		entries = cur.fetchall()
	tdlist = [dict(what_to_do=row[0], due_date=row[1], need_help=row[2], status=row[3]) for row in entries]
	return jsonify(tdlist)

@app.route("/add", methods=['POST'])
def add_item():
	if request.method == 'POST':
		with sqlite3.connect(DATABASE) as connection:
			db = connection.cursor()
			DATA = request.json
			DATA = json.loads(DATA)
			task = (DATA['what_to_do'], DATA['when_due'], DATA['need_help'],DATA['user_id'], 'not_done')
			db.execute('insert into todo (what_to_do, when_due, need_help, user_id, status) values (?, ?, ?, ?, ?)',task)
	return 'Success'


@app.route('/delete',methods=['POST'])
def del_item():
	with sqlite3.connect(DATABASE) as connection:
		db = connection.cursor()
		DATA = json.loads(request.json)
		print(DATA)
		task = (DATA['item'],DATA['user_id'])
		db.execute("DELETE FROM todo WHERE what_to_do=? AND user_id=?",task)
	return 'Success'

@app.route('/mark',methods=['POST'])
def mark_as_done():
	with sqlite3.connect(DATABASE) as connection:
		db = connection.cursor()
		DATA = json.loads(request.json)
		task = (DATA['item'],DATA['user_id'])
		cur = db.execute('SELECT status FROM todo WHERE what_to_do=? AND user_id=?',task)
		entries = cur.fetchall()
		print(entries[0][0])
		if entries[0][0] == 'not_done':
			db.execute("UPDATE todo SET status='done' WHERE what_to_do=? AND user_id=?",task)
		else:
			db.execute("UPDATE todo SET status='not_done' WHERE what_to_do=? AND user_id=?",task)
	return 'Success'

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(app.config['DATABASE'])
    return g.sqlite_db


if __name__ == "__main__":
    app.run("0.0.0.0",port=5000,debug=True)
