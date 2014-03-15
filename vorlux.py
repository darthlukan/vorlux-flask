@app.route('/register', methods=['GET', 'POST'])
def register #registering new user
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
		elif not request.form['password'] != request.form['password2']
			error = 'Passwords do not match'
		elif get_user_id(request.form['username']) is not None:
			error = 'Chosen username is already taken'
		else:
			db = get_db()
			db.execute('''insert into user (
			  username, email, pw_hash) values (?, ?, ?)''',
			  [requst.form['username'], request.form['email'],
			  generate_password_hash(request.form['password'])])
			db.commit()
			flash('Thank you for registering! You may now login')
			return redirect(url_for('login'))
	return render_template('register.html', error=error)	
