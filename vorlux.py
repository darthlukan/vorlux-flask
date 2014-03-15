#!/usr/bin/env python

import os
import sqlite3

from werkzeug.security import generate_password_hash
from flask import Flask, request, session, g, redirect, url_for, render_template, flash

from flask_mail import Mail, Message
from config import ADMINS

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

mail = Mail(app)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def get_user_id(db, username):
    rv = db.execute('''SELECT userid FROM user WHERE username = ?''', [username], one=True)
    if rv:
        return rv[0]
    return None


@app.route('/register', methods=['GET', 'POST'])
def register():  # registering new user
    # Move the db definition up here.
    db = get_db()
    if g.user:
        return redirect(url_for('members'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'Please enter a valid username'
        elif not request.form['email'] or '@' not in request.form['email']:
            error = 'Please enter a valid email address'
        elif not request.form['password']:
            error = 'Password is required'
        elif not request.form['password'] != request.form['password2']:
            error = 'Passwords do not match'
    elif get_user_id(request.form['username']) is not None:
        error = 'Chosen username is already taken'
    else:
        db.execute(
            '''INSERT INTO user (username, email, pw_hash) VALUES (?, ?, ?)''',
            [request.form['username'], request.form['email'],
             generate_password_hash(request.form['password'])]
        )
        db.commit()
        flash('Thank you for registering! You may now login')
        return redirect(url_for('/'))
    return render_template('register.html', error=error)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('/'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('/'))


@app.route('/about')
def about_us():
    return render_template('aboutus.html')


@app.route('/help')
def help_page():
    return render_template("help.html")


@app.route('/employees')
def employees():
    return render_template('employees.html')


@app.route('/plans')
def plans():
    return render_template('plans.html')


@app.route('/support')
def support():
    return render_template('support.html')


@app.route('/donate')
def donate():
    return render_template('donate.html')


def send_email(email_data):
    msg = Message(
        subject=email_data['subject'],
        sender=ADMINS[0],
        recipients=ADMINS
    )
    msg.body = """
    The user: %s with email: %s sent the following message:\n
    '%s'\n

    Message sent from contact page.\n
    """ % (email_data['name'], email_data['email'], email_data['user_message'])
    try:
        with app.app_context():
            mail.send(msg)
        return True
    except Exception, e:
        print e.message
        return False


@app.route('/contact', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        form = request.form
        email_data = {
            'email': form['email'],
            'name': form['name'],
            'subject': form['subject'],
            'user_message': form['message']
        }
        if send_email(email_data):
            flash('Message sent! We will get back to you ASAP!')
            return redirect("/")
        else:
            return render_template('contactus.html', error="Failed to send email via contact form!")
    else:
        return render_template('contactus.html')

if __name__ == '__main__':
    init_db()
    app.run(host='localhost', port=5000)
