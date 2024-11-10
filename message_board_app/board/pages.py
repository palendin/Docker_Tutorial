# As your Flask project grows, you have lots of view functions and other related bits of code that work together. 
# Instead of adding all these directly to a basic app.py file, you can create blueprints that you register in your application factory
from flask import Blueprint, render_template, url_for, redirect, request, session, flash
from .models import User
from .extensions import db

# blueprints are existing view functions
bp = Blueprint('pages', __name__)

@bp.route('/')
def index():
    if 'username' in session:
        print(session['username'])
        return render_template("pages/home.html")
    else:
        return redirect(url_for('pages.login'))

# automatically redirect users from the root URL (/) to the login page when opening the app:
@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # input fields in login.html (name="username" and name="password") defines the keys that Flask uses to extract the form data when the form is submitted. The username/password string here must correspond to them
        # Flask uses request.form to access form data submitted via a POST request.
        # When the form is submitted via a POST request, Flask collects the data in request.form, which is a dictionary-like object (e.g., {'username': 'value entered in the username field', 'password': 'value entered in the password field'}). This object holds the input values from the form fields.
        username = request.form['username'] 
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        existing_password = User.query.filter_by(password=password).first()
        
        # Validate credentials
        if existing_user and existing_password is not None: # users is a dictionary, username is key and password is value (example users = {'admin': 'admin_password', 'guest': 'guest_password'})
            session['username'] = username  # Store the username in session. Data stored in session is kept for the duration of the user's session
            session.permanent = False  # Make the session permanent = False
            return redirect(url_for('pages.home'))
        else:
            flash('Invalid credentials or account doesnt exist. Please try again.', category='error')
            return redirect(url_for("pages.login"))
    return render_template('pages/login.html')  # Renders the login form

# using the view functions to define routes
@bp.route("/home")
def home():
    if 'username' not in session:
        return redirect(url_for('pages.login'))
    return render_template("pages/home.html") # Redirect to login if not logged in (why pages.login instead of login? - because its running from __init__.py)

@bp.route("/about")
def about():
    if 'username' not in session:
        return redirect(url_for('pages.login'))
    return render_template("pages/about.html")

@bp.route("/contact")
def contact():
    if 'username' not in session:
        return redirect(url_for('pages.login'))
    return render_template("pages/contact.html")

@bp.route("/contact/contact_info")
def contact_info():
    if 'username' not in session:
        return redirect(url_for('pages.login'))
    # contact_info.html leads to a separate page
    return render_template("pages/contact_info.html")

@bp.route("/plotter")
def plotter():
    return render_template("pages/plotter.html")

@bp.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session. Session object is used to store data across requests for a particular user. Data stored in session is kept for the duration of the user's session, which is typically until they close the browser or log out.
    response = redirect(url_for('pages.login'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    return response
    #return redirect(url_for('pages.login'))
