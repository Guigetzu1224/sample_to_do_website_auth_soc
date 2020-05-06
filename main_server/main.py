from flask import Flask, render_template, redirect, g, request, url_for, jsonify, redirect
from flask import Blueprint
import sqlite3
import json
import requests
import urllib
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint
from flask import current_app as app
from flask import redirect, render_template, flash, request, session, url_for
import flask_login
import os
import sys

print(sys.argv)


AUTH_URL = "http://"+sys.argv[1]+":5000"
TODO_URL = "http://"+sys.argv[2]+":5000"
SOC_URL = "http://"+sys.argv[3] + ":5000"
#SOC_URL = "http://localhost:8000"
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'super secret string'


login_manager = flask_login.LoginManager()
login_manager.init_app(app)



#---- AUTHENTICATION ------

class User(flask_login.UserMixin):
    #Overide the get_id method
    def get_id(self):
        return self.id

def base_data():
    if flask_login.current_user.is_authenticated:
        user_id = flask_login.current_user.is_authenticated
    else:
        user_id='None'


@login_manager.user_loader
def user_loader(username):
    data = json.dumps({'username':username})
    req = requests.get(AUTH_URL+'/lookup',json=data)
    data = req.json()
    if data['1'] == 'None':
        return
    user = User()
    user.id = data['username']
    return user

@login_manager.request_loader
def request_loader(request):
    username = request.form.get("username")
    data = json.dumps({'username':username})
   # print(requests.form)
    req = requests.get(AUTH_URL+'/lookup',json=data)
    req = req.json()
    if req['1'] == 'None':
        return
    user = User()
    user.id = req['username']
    return user

@app.route("/login",methods=["POST","GET"])
def login():
    if request.method=='GET':
        return render_template('login.html')
    elif request.method=='POST':
        data = json.dumps({'username':request.form['username'],'password':request.form['password']})
        req = requests.post(AUTH_URL+'/login',json=data)
        info = req.json()
        if info['1'] == 'Authenticated':
            user = User()
            user.id = info['username']
            flash('Logged in successfully','alert alert-success')
            flask_login.login_user(user)
            return redirect(url_for('show_list'))
        flash("Incorrect Password or Username",'alert alert-warning')
        return render_template('login.html',data=base_data())

@app.route("/signup", methods=["POST","GET"])
def signup():
    if request.method=='GET':
        return render_template('signup.html')
    elif request.method=='POST':
        data = json.dumps({'user_id':request.form['username']})
        check_user = requests.get(AUTH_URL+'/lookup/exists',json=data)
        user_exists = bool(check_user.json()['1'])
        if user_exists:
            flash("That username already exists!",'alert alert-warning')
            return render_template('signup.html')
        data = json.dumps({'email':request.form['email'],'username':request.form['username'],'password':request.form['password']})
        req = requests.post(AUTH_URL+'/add',json=data)
        flash("User created successfully",'alert alert-success')
        return render_template('login.html')

@app.route("/logout")
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('show_list'))



#---- MAIN APP ------


@app.route("/")
def show_list():
    #    entry = {'id':flask_login.current_user.id,'status':'logged_in'}
    if flask_login.current_user.is_authenticated:
        info = json.dumps({'user_id':flask_login.current_user.id})
    else:
        info = json.dumps({'user_id':"None"})
    print('Hi there')
    resp = requests.get(TODO_URL+'/api/items',json=info)
    resp = resp.json()
    if flask_login.current_user.is_authenticated:
        data = {'to_do':resp,'user_id':flask_login.current_user.id}
    else:
        data = {'to_do':resp,'user_id':"None"}
    #Getting familys to do list
    if data['user_id'] != "None":
        data['family_member_to_do'] = []
        temp_data = json.dumps({'user_id':flask_login.current_user.id})
        fam_resp = requests.get(SOC_URL+'/family',json=temp_data)
        fam_resp = fam_resp.json()
        if 'list_of_members' in fam_resp:
            for fam_member in fam_resp['list_of_members']:
                new_info = json.dumps({'user_id':fam_member['members']})
                info_2  = requests.get(TODO_URL+'/api/items',json=new_info)
                info_2 = info_2.json()
                data['family_member_to_do'].append({'family_member':fam_member['members'],'to_do':info_2})
    return render_template('index.html', data=data)

@app.route("/add", methods=['POST'])
def add_entry():
    if flask_login.current_user.is_authenticated:
        user_id = flask_login.current_user.id
    else:
        user_id = 'None'
    if 'need_help' in request.form:
        data =json.dumps({'what_to_do':request.form['what_to_do'],'when_due':request.form['due_date'],'need_help':request.form['need_help'],'user_id':user_id})
    else:
        data = json.dumps({'what_to_do':request.form['what_to_do'],'when_due':request.form['due_date'],'need_help':'no','user_id':user_id})
    req=requests.post(TODO_URL+'/add',json=data)
    return redirect(url_for('show_list'))

@app.route("/lookup",methods=["POST"])
@flask_login.login_required
def lookup():
    #Checking if the user exists
    data = json.dumps({'user_id':request.form['user_id']})
    check_user = requests.get(AUTH_URL+'/lookup/exists',json=data)
    user_exists = bool(check_user.json()['1'])
    if user_exists:
        req = requests.get(TODO_URL+'/api/items',json=data)
        resp = req.json()
        data = {'to_do':resp,'user_id':request.form['user_id']}
        #resp['user_id'] = request.form['user_id']
        return render_template('index_search.html',data=data)
    else:
        flash("That user does not exist!",'alert alert-warning')
        return redirect(url_for('show_list'))


@app.route("/delete/<item>")
def delete_entry(item):
    if flask_login.current_user.is_authenticated:
        user_id = flask_login.current_user.id
    else:
        user_id = 'None'
    data = json.dumps({'item':item,'user_id':user_id})    
    req = requests.post(TODO_URL+'/delete',json=data)
    return redirect(url_for('show_list'))


@app.route("/mark/<item>")
def mark_as_done(item):
    if flask_login.current_user.is_authenticated:
        user_id = flask_login.current_user.id
    else:
        user_id = 'None'
    data = json.dumps({'item':item,'user_id':user_id}) 
    req = requests.post(TODO_URL+'/mark',json=data)
    return redirect(url_for('show_list'))


# ----- SOCIAL MEDIA SECTION -----
@app.route("/profile/<user_id>")
@flask_login.login_required
def profile(user_id):
    if flask_login.current_user.is_authenticated:
        user_id_curr = flask_login.current_user.id
        if user_id != user_id_curr:
            redirect(url_for('login'))
        data = json.dumps({'user_id':user_id})
        print(user_id)
        req = requests.get(SOC_URL+'/family',json=data)
        data = req.json()
        data['user_id'] = user_id
    return render_template('profile.html',data=data)


@app.route("/family/myfamily/<user_id>",methods=["GET"])
@flask_login.login_required
def family_manager(user_id):
    if flask_login.current_user.is_authenticated:
        user_id_curr = flask_login.current_user.id
        if user_id != user_id_curr:
            redirect(url_for('login'))
        data = json.dumps({'user_id':user_id})
        print(user_id)
        req = requests.get(SOC_URL+'/family',json=data)
        data = req.json()
        data['user_id'] = user_id
        pend_req = requests.get(SOC_URL+'/add/pending',json=json.dumps({'user_id':user_id}))
        pend_req = pend_req.json()
        try:
            pending_id = pend_req['Pending'][0]
            pending_id = [str(x) for x in pending_id.split(',')]
            data['pending_family_id'] = pending_id
        except:
            data['pending_family_id'] ={'Null':'Null'}
    return render_template('family.html',data=data)


@app.route("/family/add/<user_id>",methods=["POST"])
@flask_login.login_required
def family_add(user_id):    
    if flask_login.current_user.is_authenticated:
        user_id_curr = flask_login.current_user.id
        if user_id == request.form['username']:
            flash('You cant add yourself!','alert alert-warning')
            redirect(url_for('show_list'))
        data = json.dumps({'user_id':request.form['username']})
        check_user = requests.get(AUTH_URL+'/lookup/exists',json=data)
        user_exists = bool(check_user.json()['1'])
        if user_exists:
            data = json.dumps({'user_id':user_id,'pending_family_id':request.form['username']})
            req = requests.post(SOC_URL+'/add',json=data)
            flash("Family member added!",'alert alert-success')
            return redirect(url_for('show_list'))
        flash("That user does not exist!",'alert alert-warning')
        return redirect(url_for('show_list'))
        
    


@app.route("/family/confirm/<user_id>/<entry>")
@flask_login.login_required
def family_confirm(user_id,entry):
    if flask_login.current_user.is_authenticated:
        user_id_curr = flask_login.current_user.id
        if user_id != user_id_curr:
            redirect(url_for('login'))
        data = json.dumps({'user_id':user_id,'pending_family_id':entry})
        req = requests.post(SOC_URL+'/add/confirm',json=data)
    return redirect(url_for('show_list'))

@app.route("/family/delete/<user_id>/<entry>")
@flask_login.login_required
def family_denied(user_id,entry):
    if flask_login.current_user.is_authenticated:
        user_id_curr = flask_login.current_user.id
        if user_id != user_id_curr:
            redirect(url_for('login'))
        data = json.dumps({'user_id':user_id,'pending_family_id':entry})
        print(data)

        req = requests.post(SOC_URL+'/add/delete',json=data)
        return redirect(url_for('show_list'))
    return redirect(url_for('login'))


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(app.config['DATABASE'])
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


if __name__ == "__main__":
    context = ('server.crt', 'server.key')#certificate and key files
    app.run("0.0.0.0",port=5000,debug=True)

