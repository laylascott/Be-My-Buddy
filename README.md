Hi, Anya the following steps should get your repository code, as it stands, working.

1. Move all HTML code into a folder named `templates`
2. Move all CSS and assets (like images) need to be moved to a folder named `static`
3. Delete lines 9 through 11 in `app.py`
    These lines are commands that should be run in the terminal.
    Run them in order (and do not copy the $)
    ```
    $ flask db init
    $ flask db migrate
    $ flask db upgrade
    ```
4. 

### How to Connect Python Flask to HTML and CSS
 1. 
 2. all CSS and assets need to be moved to a folder named `static`
 3. To connect CSS to HTML add this link to the `<head>` tag of all HTML files.
    ```
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    ```

### Database Set Up
Before your app will work ensure you have run the following commands on your local machine, in the terminal *(This only needs to be done once to create and set up your database)*
*Note: do not include the `$`*
```
$ flask db init
$ flask db migrate
$ flask db upgrade
```

### Running in Debug
To run your app in debug mode on a local server you can run
```
python app.py
```
### Stopping Debug
Type `ctrl + C` in the terminal

---

### Fixing LogIn and SignUp

#### Login:
There was NO issue with your login function. 

*The one provided below also works just with a different functionality. It will tell the user whether their username or password is wrong. If both are wrong it will default to saying the username is wrong.*
```
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password, password):
                session['user_id'] = user.id
                flash(f'Welcome, {username}!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Incorrect password', 'danger')
        else:
         
            flash('Incorrect username', 'danger')

    return render_template('login.html')

```
Here is a sample login.html
```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='login.css') }}">
</head>
<body>
    <div class="container">
        <h2>Login</h2>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="POST" action="{{ url_for('login') }}">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Login</button>
        </form>
        <p>Don't have an account? <a href="{{ url_for('signup') }}">Sign up</a></p>
    </div>
</body>
</html>

```

#### SignUp
It appears that the only issue with your signup is that you should `return render_template('signup.html', form=form)` everytime you check the database.
```
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        phone_number = form.phone_number.data
        password = form.password.data

        # Check if the username is already taken
        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Please choose a different one.', 'danger')
            return render_template('signup.html', form=form)
        
        # Check if the email is already taken
        if User.query.filter_by(email=email).first():
            flash('Email is already registered. Please choose a different one.', 'danger')
            return render_template('signup.html', form=form)
        
        # Check if the phone number is already taken
        if User.query.filter_by(phone_number=phone_number).first():
            flash('Phone number is already registered. Please choose a different one.', 'danger')
            return render_template('signup.html', form=form)

        # Create a new user
        new_user = User(username=username, email=email, phone_number=phone_number,
                        password=generate_password_hash(password, method='pbkdf2:sha1'))
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)
```
As for the html, you have a Sign Up on the ho

