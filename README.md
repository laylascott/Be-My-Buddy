Hi, Anya the following steps should get your repository code, as it stands, working.

1. Move all HTML code into a folder named `templates`
2. Move all CSS and assets (like images) to a folder named `static`

   Your file structure should look like this when you are done:
   
   ![Screenshot of file structure](/filestruct.png).
4. Delete lines 9 through 11 in `app.py`
     -   _These lines are commands that should be run in the terminal. I will instruct you how to do that in just a moment._
5. Delete line 8 (it is never used)
6. Add the following import `from flask_migrate import Migrate`
7. On line 17 add `migrate = Migrate(app, db)` to use the import we just added.
8. You may delete lines 18 and 19 they will not be used later.
9. Line 70 should be replaced with the following:
    ```python
    with app.app_context():
    db.create_all()
    ```
10. Now we need to run the commands to intialize the database
    Run them in order (and do not copy the $)
    ```sh
    $ flask db init
    $ flask db migrate
    $ flask db upgrade
    ```
11. You will see new files and objects were created. This is a good sign!
__Now your database is intialized and ready to be used.__

__We are going to switch over to adjusting the HTML code now__
1. In the `<head>` tag of all your HTML files replace the current style tag with this one: `<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">`. This just uses the flask convention to link your css file.
2. Your navbar class should be replaced with this one:
```html
<nav class="navbar">
      <ul>
        <li><a href="{{ url_for('home') }}">Home</a></li>
        <li><a href="{{ url_for('about') }}">About</a></li>
        <li><a href="{{ url_for('availability') }}">Set Availability</a></li>
        <li><a href="{{ url_for('report') }}">Report</a></li>
    </ul>
    </nav> 
```
3. Your `index.html` does not currently connect your form to your database. The code below is how to connect the form
``` html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home | Be My Buddy</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>Be My Buddy</h1>

    <nav class="navbar">
        <ul>
            <li><a href="{{ url_for('home') }}">Home</a></li>
            <li><a href="{{ url_for('about') }}">About</a></li>
            <li><a href="{{ url_for('availability') }}">Set Availability</a></li>
            <li><a href="{{ url_for('report') }}">Report</a></li>
        </ul>
    </nav>

    <div class="container">
        <div class="form-box">
            <h1 id="title">Sign Up</h1>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            <form method="POST" action="{{ url_for('home') }}">
                {{ signup_form.csrf_token }}
                <div class="input-group">
                    <div class="input-field" id="nameField">
                        {{ signup_form.username(class="form-control", placeholder="Username") }}
                    </div>
                    <div class="input-field" id="emailField">
                        {{ signup_form.email(class="form-control", placeholder="Email") }}
                    </div>
                    <div class="input-field" id="numberField">
                        {{ signup_form.phone_number(class="form-control", placeholder="Phone Number") }}
                    </div>
                    <div class="input-field">
                        {{ signup_form.password(class="form-control", placeholder="Password") }}
                    </div>
                    <div class="input-field" id="confirmPasswordField">
                        {{ signup_form.confirm_password(class="form-control", placeholder="Confirm Password") }}
                    </div>
                </div>
                <br><br>
                <div class="btn-field">
                    <button type="submit" name="action" value="signup" id="signupBtn" class="btn btn-primary">Sign Up</button>
                    <button type="button" id="toggleToSigninBtn" class="btn btn-secondary">Sign In</button>
                </div>
            </form>

            <form method="POST" action="{{ url_for('home') }}" id="loginForm" style="display: none;">
                {{ login_form.csrf_token }}
                <div class="input-group">
                    <div class="input-field">
                        {{ login_form.username(class="form-control", placeholder="Username") }}
                    </div>
                    <div class="input-field">
                        {{ login_form.password(class="form-control", placeholder="Password") }}
                    </div>
                </div>
                <br><br>
                <div class="btn-field">
                    <button type="button" id="toggleToSignupBtn" class="btn btn-secondary">Sign Up</button>
                    <button type="submit" name="action" value="login" class="btn btn-primary">Sign In</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        let signupBtn = document.getElementById("signupBtn");
        let toggleToSigninBtn = document.getElementById("toggleToSigninBtn");
        let toggleToSignupBtn = document.getElementById("toggleToSignupBtn");
        let nameField = document.getElementById("nameField");
        let emailField = document.getElementById("emailField");
        let numberField = document.getElementById("numberField");
        let confirmPasswordField = document.getElementById("confirmPasswordField");
        let title = document.getElementById("title");
        let signupForm = document.querySelector("form[action='{{ url_for('home') }}']");
        let loginForm = document.getElementById("loginForm");

        toggleToSigninBtn.onclick = function () {
            nameField.style.display = "none";
            emailField.style.display = "none";
            numberField.style.display = "none";
            confirmPasswordField.style.display = "none";
            title.innerHTML = "Sign In";
            signupForm.style.display = "none";
            loginForm.style.display = "block";
        };

        toggleToSignupBtn.onclick = function () {
            nameField.style.display = "block";
            emailField.style.display = "block";
            numberField.style.display = "block";
            confirmPasswordField.style.display = "block";
            title.innerHTML = "Sign Up";
            signupForm.style.display = "block";
            loginForm.style.display = "none";
        };
    </script>
</body>
</html>
```

__We are almost ready to run your app__
Just a few more steps back in `app.py`
We want to delete your current
``` python
@app.route('/')
@app.route('/signup', methods=['GET', 'POST']
@app.route('/login', methods=['GET', 'POST'])
```

and replace it with the following:
``` python
@app.route('/', methods=['GET', 'POST'])
def home():
    signup_form = SignupForm()
    login_form = LoginForm()

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'signup' and signup_form.validate_on_submit():
            username = signup_form.username.data
            email = signup_form.email.data
            phone_number = signup_form.phone_number.data
            password = signup_form.password.data

            # Check if the username is already taken
            if User.query.filter_by(username=username).first():
                flash('Username is already taken. Please choose a different one.', 'danger')
            elif User.query.filter_by(email=email).first():
                flash('Email is already registered. Please choose a different one.', 'danger')
            elif User.query.filter_by(phone_number=phone_number).first():
                flash('Phone number is already registered. Please choose a different one.', 'danger')
            else:
                new_user = User(username=username, email=email, phone_number=phone_number,
                                password=generate_password_hash(password, method='pbkdf2:sha1'))
                db.session.add(new_user)
                db.session.commit()
                flash('Account created successfully! You can now log in.', 'success')
                return redirect(url_for('home'))

        elif action == 'login' and login_form.validate_on_submit():
            username = login_form.username.data
            password = login_form.password.data

            user = User.query.filter_by(username=username).first()

            if user:
                if check_password_hash(user.password, password):
                    session['user_id'] = user.id
                    flash(f'Welcome, {username}!', 'success')
                    return redirect(url_for('availability'))
                else:
                    flash('Incorrect password', 'danger')
            else:
                flash('Incorrect username', 'danger')

    return render_template('index.html', signup_form=signup_form, login_form=login_form)

@app.route('/availability')
def availability():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        time_slots = user.time_slots
        return render_template('availability.html', time_slots=time_slots, username=user.username)
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/report')
def report():
    return render_template('report.html')

```
This code combined your signup and login logic all into the index app route for better style and simplicty when reaching the provided forms. It also creates routes to your other pages so we can access them in the nav bar.

Those changes should do it. To see your code in action got to the terminal and type `python app.py` you should be given a link like this `* Running on http://127.0.0.1:5000` to follow. If this ever gives you issues you can also run `flask run -p 4000`. This just runs the program on a different local port.
