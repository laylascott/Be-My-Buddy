from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators
from werkzeug.local import LocalProxy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate




app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Use SQLite for simplicity
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)


# Example user data (for demonstration purposes)
users = {'user1': generate_password_hash('password1'), 'user2': generate_password_hash('password2')}




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    time_slots = db.relationship('TimeSlot', backref='user', lazy=True)
    reports_received = db.relationship('Report', backref='reported_user', lazy=True, foreign_keys='Report.reported_user_id')
    reports_sent = db.relationship('Report', backref='reporting_user', lazy=True, foreign_keys='Report.reporting_user_id')


class SignupForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=50)])
    email = StringField('Email', [validators.Email()])
    phone_number = StringField('Phone Number', [validators.Regexp(r'^\d{10}$', message='Invalid phone number.')])
    password = PasswordField('Password', [validators.Length(min=6, max=200)])
    confirm_password = PasswordField('Confirm Password', [
        validators.EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.InputRequired()])
    password = PasswordField('Password', [validators.InputRequired()])
    submit = SubmitField('Login')


class TimeSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(20), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.Text, nullable=False)
    reporting_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


with app.app_context():
    db.create_all()

@app.route('/')
def home():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        time_slots = user.time_slots
        users = User.query.all()
        return render_template('index.html', time_slots=time_slots, username=user.username, users=users)

    return redirect(url_for('login'))  # Redirect to login only if user is not logged in



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
            flash('Username is already taken. Please choose a different one.', 'Username is already taken')
            return render_template('signup.html', form=form)

        # Create a new user
        new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha1'))
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('home'))

    return render_template('signup.html', form=form)




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        print("User:", user)  # Debug statement

        if user:
            print("Stored Password Hash:", user.password)  # Debug statement
            print("Entered Password Hash:", generate_password_hash(password))  # Debug statement

        if user and check_password_hash(user.password, password):
            # Successful login
            flash(f'Welcome, {username}!', 'success')
            return redirect(url_for('home'))
        else:
            # Invalid login
            return redirect(url_for('home'))

    return render_template('login.html')




#for users who are volunteering their time to get others home safely
@app.route('/book/<int:time_slot_id>')
def book(time_slot_id):
    time_slot = TimeSlot.query.get(time_slot_id)

    if time_slot and time_slot.is_available:
        time_slot.is_available = False
        db.session.commit()
        flash(f'Time slot "{time_slot.time}" booked successfully!', 'success')
    else:
        flash('Invalid or already booked time slot.', 'danger')

    return redirect(url_for('home'))


#for people to see who is available to walk with them
@app.route('/user/<int:user_id>')
def user_availability(user_id):
    user = User.query.get(user_id)

    if user:
        return render_template('user_availability.html', user=user)

    flash('User not found', 'danger')
    return redirect(url_for('home'))



@app.route('/volunteer')
def volunteer_home():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        time_slots = user.time_slots
        users = User.query.all()
        return render_template('volunteer_home.html', time_slots=time_slots, username=user.username, users=users)

    return redirect(url_for('login'))

@app.route('/seeker')
def seeker_home():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        return render_template('seeker_home.html', username=user.username)

    return redirect(url_for('login'))


    
@app.route('/report_user/<int:reported_user_id>', methods=['POST'])
def report_user(reported_user_id):
    if 'user_id' in session:
        reporting_user_id = session['user_id']
        reported_user = User.query.get(reported_user_id)

        if reported_user:
            if request.method == 'POST':
                if 'submit' in request.form:
                    reason = request.form.get('reason')

                    if reason:
                        new_report = Report(reason=reason, reporting_user_id=reporting_user_id, reported_user_id=reported_user_id)
                        db.session.add(new_report)
                        db.session.commit()
                        flash('User reported successfully!', 'success')
                    else:
                        flash('Reason cannot be empty', 'danger')

                return redirect(url_for('home'))

            return render_template('report_user.html', reported_user=reported_user)

        flash('User not found', 'danger')

    return redirect(url_for('login'))





@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True



if __name__ == '__main__':
    app.run(debug=True)
