# This is a simple example web app that is meant to illustrate the basics.
from flask import Flask, render_template, redirect, g, request, url_for, jsonify
import sqlite3
import json
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = 'users.db'
app = Flask(__name__)
app.config.from_object(__name__)


def check_if_user_exists(username):
	with sqlite3.connect(DATABASE) as connection:
		db = connection.cursor()
		task = (username,)
		results = db.execute('SELECT username FROM users WHERE username=?',task).fetchall()
		if len(results) == 0 :
			return False
		return True

@app.route("/login",methods=['POST'])
def get_items():
	with sqlite3.connect(DATABASE) as connection:
		db = connection.cursor()
		DATA = request.json
		DATA = json.loads(DATA)
		task = (DATA['username'],DATA['password'])
		print(task)
		cur = db.execute('SELECT username, user_id, password FROM users WHERE username="'+str(DATA['username'])+'"')
		cur = cur.fetchall()
		if len(cur) == 0:
			return jsonify({'1':"User Dosn't Exist"})
		password = cur[0][2]
		if check_password_hash(password,DATA['password']):		
			tdlist = {'1':'Authenticated','username':cur[0][0],'user_id':cur[0][1]}
			return jsonify(tdlist)
		else:
			return jsonify({'1':'Incorrect Password'})

@app.route("/add", methods=['POST'])
def add_item():
	if request.method == 'POST':
		with sqlite3.connect(DATABASE) as connection:
			db = connection.cursor()
			DATA = request.json
			DATA = json.loads(DATA)
			task = (DATA['email'], DATA['username'], generate_password_hash(DATA['password']))
			is_present = db.execute('SELECT email FROM users WHERE email="'+str(DATA['email'])+'"')
			is_present = is_present.fetchall()
			if len(is_present) == 0:
				db.execute('INSERT INTO users (email, username, password) values (?, ?, ?)',task)
			else:
				return jsonify({"User Already Exists":1})
	return 'Success'

@app.route("/lookup",methods=['GET'])
def lookup():
	with sqlite3.connect(DATABASE) as connection:
		db = connection.cursor()
		DATA = request.json
		DATA = json.loads(DATA)
		task = (DATA['username'],)
		print(DATA)
		cur = db.execute('SELECT username, email, user_id, password FROM users WHERE username=?',task)
		cur = cur.fetchall()
		if len(cur) == 0:
			return jsonify({'1':"None"})
		email = cur[0][1]
		return jsonify({'1':'True','email':email,'username':cur[0][0]})

@app.route("/lookup/exists",methods=['GET'])
def exists():
	DATA = request.json
	DATA = json.loads(DATA)
	user_exists = check_if_user_exists(DATA['user_id'])
	return jsonify({'1':user_exists})

if __name__ == "__main__":
    app.run("0.0.0.0",port=5000,debug=True)
