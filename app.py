import re
import json
from flask import Flask, render_template, redirect, url_for, session, request
from bson import ObjectId # ObjectId to work
from pymongo import MongoClient
# import os

app = Flask(__name__)
app.secret_key = '123a'
client = MongoClient("mongodb://127.0.0.1:27017")
db = client.flaskpyappdb # Selects the db
userCollection = db.users # Selects the collection


@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # extract all form fields
        username = request.form['username']
        password = request.form['password']
        account = userCollection.find_one({'username':username})
        if account:
            # print(ObjectId(account['_id']))
            session['loggedin'] = True
            # session['id'] = json.dumps(ObjectId(account['_id']), indent=4)
            session['username'] = account['username']
            print('successfully loggedin')
            return redirect(url_for('home'))
        elif not username or not password:
            msg = 'Please fill out the form!'
        else:
            msg = 'Incorrect username or password'
    # return error msg
    return render_template('index.html', msg=msg)

if __name__ == '__main__':
    app.run(debug=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form:
        # extract all form fields
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            account = userCollection.find_one({'$or': [{'username':username}, {'email':email}]})
            if account:
                msg='Account already exists'
            else:
                userCollection.insert_one({'username':username, 'email':email, 'password':password})
                msg = 'You have successfully registered!'
    
    elif request.method == 'POST':
        msg='Please, all fields are required'
    # return error msg
    return render_template('register.html', msg=msg)


@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    if 'loggedin' in session:
        account = userCollection.find_one({'username':session['username']})
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    # redirect to login page
    return redirect(url_for('login'))