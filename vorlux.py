from flask import g, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from flaskr import app, get_db, request, render_template


# Modify the original that wasn't included in this file so that it
# takes the db object created in the register function as an arg.
# Use that to make our query.
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
