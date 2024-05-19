from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, SubmitField, validators
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
migrate = Migrate(app, db)

csrf.init_app(app)

logging.basicConfig(level=logging.DEBUG)

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
