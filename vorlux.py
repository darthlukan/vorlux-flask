#!/usr/bin/env python

import sqlite3
import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from werkzeug.security import generate_password_hash

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
            '''insert into user (username, email, pw_hash) values (?, ?, ?)''',
            [request.form['username'], request.form['email'],
            generate_password_hash(request.form['password'])]
        )
        db.commit()
        flash('Thank you for registering! You may now login')
        return redirect(url_for('login'))
    return render_template('register.html', error=error)

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('SELECT title, text FROM entries ORDER BY id DESC')
    entries = cur.fetchall()
    return render_template('base_layout.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('INSERT INTO entries (title, text) VALUES (?, ?)',
               [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


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
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


@app.route('/help')
def help_page():
    return render_template("help.html")


if __name__ == '__main__':
    init_db()
    app.run(host='10.0.0.5', port=5000)
