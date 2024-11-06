# adding additional functionality to the login app

from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta

app = Flask(__name__)

# Secret key for session management (necessary for using sessions)
app.secret_key = 'your_secret_key'

# Dummy user credentials for login
users = {
    "admin": "adminpassword",  # Admin credentials
    "guest": "guestpassword"   # Guest credentials
}

# Set session lifetime to 30 minutes (this dictates the duration of the user's session before logging out)
app.permanent_session_lifetime = timedelta(minutes=30)

# automatically redirect users from the root URL (/) to the login page when opening the app:
@app.route('/')
def home():
    return redirect(url_for('login'))

# Login route (for handling login form submissions)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # input fields in login.html (name="username" and name="password") defines the keys that Flask uses to extract the form data when the form is submitted. The username/password string here must correspond to them
        # Flask uses request.form to access form data submitted via a POST request.
        # When the form is submitted via a POST request, Flask collects the data in request.form, which is a dictionary-like object (e.g., {'username': 'value entered in the username field', 'password': 'value entered in the password field'}). This object holds the input values from the form fields.
        username = request.form['username'] 
        password = request.form['password']
        
        # Validate credentials
        if username in users and users[username] == password: # users is a dictionary, username is key and password is value (example users = {'admin': 'admin_password', 'guest': 'guest_password'})
            session['username'] = username  # Store the username in session. Data stored in session is kept for the duration of the user's session
            session.permanent = False  # Make the session permanent = False
            if username == 'admin':
                return redirect(url_for('hello_admin'))
            else:
                return redirect(url_for('hello_guest', guest=username))
        else:
            return 'Invalid credentials. Please try again.'
    return render_template('login.html')  # Renders the login form

# Guest greeting route
@app.route('/guest/<guest>')
def hello_guest(guest):
    if 'username' in session and session['username'] == guest: # Data stored in session is kept for the duration of the user's session
        return f'Hello {guest}, you are a guest'
    else:
        return redirect(url_for('login'))  # Redirect to login if not logged in

# Admin greeting route
@app.route('/admin')
def hello_admin():
    if 'username' in session and session['username'] == 'admin': # Data stored in session is kept for the duration of the user's session
        return 'Hello Admin'
    else:
        return redirect(url_for('login'))  # Redirect to login if not logged in

# Additional route after login (e.g., user dashboard)
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        return f'Welcome to your dashboard, {username}!'
    else:
        return redirect(url_for('login'))  # Redirect to login if not logged in

# Logout route to clear the session
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session. Session object is used to store data across requests for a particular user. Data stored in session is kept for the duration of the user's session, which is typically until they close the browser or log out.
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)