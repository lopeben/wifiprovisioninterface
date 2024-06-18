#! /usr/bin/python
import os

from wifisupplicant import restart_networking, update_wpa_supplicant

# Importing necessary modules from flask, wtforms and werkzeug
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, PasswordField, SubmitField
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


ACCESSPOINT_IP = '192.168.4.1'

# Initialize Flask app
app = Flask(__name__)

# Setting a random secret key for the Flask application
app.config['SECRET_KEY'] = os.urandom(24)

# Initialize Login Manager
login_manager = LoginManager()
# Setting up the login manager for the app
login_manager.init_app(app)
# Specifying the view to redirect to when the user needs to log in.
login_manager.login_view = 'login'

# User data would be stored in a database in a real application
# For this example, a dictionary is used to store user data
users = {'user': generate_password_hash('password')}


# Defining a User class with UserMixin for user session management
class User(UserMixin):
    def __init__(self, username):
        self.id = username


# This callback is used to reload the user object from the user ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)


# Defining a form for login using FlaskForm
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# Defining the login view
@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # If form is submitted and validated
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # If the username exists and password is correct
        if username in users and check_password_hash(users[username], password):
            user = User(username)
            # Log the user in
            login_user(user)
            # Redirect to the protected route
            return redirect(url_for('wifiprovision'))
        # If login details are incorrect, show an error message
        flash('Login Unsuccessful. Please check username and password', 'danger')
    # Render the login template
    return render_template('login.html', form=form)


@app.route('/wifiprovision')
@login_required
def wifiprovision():
    return render_template('wifiprovision.html')


@app.route('/wifisecrets', methods=['POST'])
def wifisecrets():
    ssid = request.form.get('ssid')
    password = request.form.get('password')

    # Update wpa_supplicant file in Raspberry Pi
    update_wpa_supplicant(ssid, password)

    return redirect(url_for('restart'))


# Defining a protected route that requires login
@app.route('/restart')
@login_required
def restart():

    # Stop existing wpa_supplicant processes
    restart_networking()

    # Return the username of the logged in user
    return f'Received WiFi Secrets. Restarting network.'


# Defining a route to log out the user
@app.route('/logout')
@login_required
def logout():
    # Log out the user
    logout_user()
    return redirect(url_for('login'))


# Running the Flask app
if __name__ == "__main__":
    app.run(debug=True, host=ACCESSPOINT_IP, port=8080)
