# This is a simple example web app that is meant to illustrate the basics.
from flask import Flask, render_template, redirect, g, request, url_for, jsonify
import sqlite3
import json

DATABASE = 'family.db'
app = Flask(__name__)
app.config.from_object(__name__)

#Get all tied family members
@app.route("/family",methods=['GET','POST'])
def get_items():
	with sqlite3.connect(DATABASE) as connection:
		db = connection.cursor()
		DATA = request.json
		DATA = json.loads(DATA)
		user_id = DATA['user_id']
		cur = db.execute('SELECT family_id FROM family WHERE user_id="'+user_id+'"')
		entries = cur.fetchall()
		if len(entries) == 0:
			print('firing')
			return jsonify({'1':'NO FAMILY  MEMBERS'})
		else:
			tdlist = {'list_of_members':None}
			tdlist['list_of_members'] = [{'members':entry} for entry in entries[0][0].split(',')]
			print(tdlist)
			return jsonify(tdlist)

#Add a family member
@app.route("/add", methods=['POST'])
def add_item():
	if request.method == 'POST':
		with sqlite3.connect(DATABASE) as connection:
			db = connection.cursor()
			DATA = request.json
			DATA = json.loads(DATA)
			# Checking whether the entry exists - if it dosnt then we add it
			task = (DATA['user_id'],'','')
			check_task = (DATA['user_id'],)
			check_if_in_list = db.execute('SELECT user_id FROM family WHERE user_id=?',check_task).fetchall()
			if len(check_if_in_list)==0:
				db.execute("INSERT INTO family (user_id,family_id,pending_family_id) VALUES (?,?,?)",task)
			# Checking if they are already friends or pending a friendship 
			task = (DATA['user_id'],'%'+str(DATA['pending_family_id'])+'%')
			check_if_friends = db.execute("SELECT user_id FROM family WHERE user_id=? AND pending_family_id LIKE ?",task).fetchall()
			check_if_pending = db.execute("SELECT user_id FROM family WHERE user_id=? AND family_id LIKE ?",task).fetchall()
			task_2 = (DATA['pending_family_id'],'%'+str(DATA['user_id'])+'%')
			check_if_other_pending = db.execute("SELECT user_id FROM family WHERE user_id = ? AND pending_family_id LIKE ?",task_2).fetchall()
			print(check_if_other_pending)
			if len(check_if_friends) != 0 or len(check_if_pending) != 0 or len(check_if_other_pending) !=0 :
				return jsonify({'1':'Already Friends or pending friendship'})
			#Now add on the new friend to that perrsons pending list
			cur_family = db.execute('SELECT user_id FROM family WHERE  user_id="'+str(DATA['pending_family_id'])+'"').fetchall()
			if len(cur_family)==0:
				task = (DATA['pending_family_id'],'',DATA['user_id'])
				db.execute('INSERT INTO family (user_id,family_id,pending_family_id) VALUES (?,?,?)',task)
			else:
				cur_pending_list = db.execute('SELECT pending_family_id FROM family WHERE user_id="'+DATA['pending_family_id']+'"').fetchall()[0][0]
				#print(cur_pending_list)
				sets = (cur_pending_list+','+DATA['user_id'],DATA['pending_family_id'])
				db.execute('UPDATE family SET pending_family_id = ? WHERE user_id = ?',sets)
	return 'Success'


#Get list of pending family members
@app.route('/add/pending',methods=["GET","POST"])
def get_pending():
	if request.method=="GET":
		with sqlite3.connect(DATABASE) as connection:
			db = connection.cursor()
			DATA = request.json
			DATA = json.loads(DATA)
			get_pending_friends = db.execute('SELECT pending_family_id FROM family WHERE user_id="'+DATA['user_id']+'"').fetchall()
			try:
				pending_friends = jsonify({'Pending':get_pending_friends[0]})
				print(pending_friends)
			except:
				pending_friends = jsonify({'Pending':[]})
			return pending_friends

@app.route('/add/confirm',methods=["GET","POST"])
def confirm_item():
	with sqlite3.connect(DATABASE) as connection:
		db = connection.cursor()
		DATA = request.json
		DATA = json.loads(DATA)
		sets = ()
		# This whole block updates the SQL rows to move over the user from pending to confirmed
		new_id = DATA['pending_family_id']
		cur_family = db.execute('SELECT family_id FROM family WHERE user_id="'+DATA['user_id']+'"').fetchall()[0][0]
		pend_family = db.execute('SELECT pending_family_id FROM family WHERE user_id="'+DATA['user_id']+'"').fetchall()[0][0]
		pend_family = [x for x in pend_family.split(',') if x != new_id]
		new_pending_family_mem = ''
		for member in pend_family:
			new_pending_family_mem += member + ','
		new_pending_family_mem = new_pending_family_mem.strip(',')
		print(new_pending_family_mem)
		if len(cur_family)==0:
			sets = (DATA['pending_family_id'],DATA['user_id'])
			db.execute('UPDATE family SET family_id = ? WHERE user_id = ?',sets)
		else:
			new_list = cur_family + ',' + DATA['pending_family_id']
			sets = (new_list,DATA['user_id'])
			db.execute('UPDATE family SET family_id = ? WHERE user_id = ?',sets)
		sets = (new_pending_family_mem,DATA['user_id'])
		db.execute('UPDATE family SET pending_family_id = ? WHERE user_id = ?',sets)
		#We now need to move this as well in the other user
		new_id = DATA['pending_family_id']
		cur_family = db.execute('SELECT family_id FROM family WHERE user_id="'+DATA['pending_family_id']+'"').fetchall()[0][0]
		cur_family = cur_family.split(',')
		cur_family.append(DATA['user_id'])
		new_pending_family_mem = ''
		for member in cur_family:
			new_pending_family_mem += member + ','
		new_pending_family_mem = new_pending_family_mem.strip(',')
		sets = (new_pending_family_mem,DATA['pending_family_id'])
		print(sets)
		db.execute('UPDATE family SET family_id = ? WHERE user_id = ?',sets)
		return "Success"
		#db.execute('UPDATE family SET family_id = ? WHERE user_id = ?', sets)


@app.route('/add/delete',methods=['POST'])
def delete_item():
	if request.method=='POST':
		with sqlite3.connect(DATABASE) as connection:
			db = connection.cursor()
			DATA = request.json
			DATA = json.loads(DATA)
			sets = ()
			#This just gets current string strips the value and then repastes it
			new_id = DATA['pending_family_id']
			pend_family = db.execute('SELECT pending_family_id FROM family WHERE user_id="'+DATA['user_id']+'"').fetchall()[0][0]
			pend_family = [x for x in pend_family.split(',') if x != new_id]
			new_pending_family_mem = ''
			for member in pend_family:
				new_pending_family_mem += member + ','
			new_pending_family_mem = new_pending_family_mem.strip(',')
			print('-'*20)
			print(pend_family)
			sets = (new_pending_family_mem,DATA['user_id'])
			print(sets)
			db.execute('UPDATE family SET pending_family_id = ? WHERE user_id = ?',sets)
			return "Success"


if __name__ == "__main__":
	app.run("0.0.0.0",port=5000,debug=True)
