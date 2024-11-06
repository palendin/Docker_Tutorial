# As your Flask project grows, you have lots of view functions and other related bits of code that work together. 
# Instead of adding all these directly to a basic app.py file, you can create blueprints that you register in your application factory
from flask import Blueprint, render_template

# blueprints are existing view functions
bp = Blueprint('pages', __name__)

# using the view functions to define routes
@bp.route("/")
def home():
    return render_template("pages/home.html") #looks for the html files in /board/templates

@bp.route("/about")
def about():
    return render_template("pages/about.html")

@bp.route("/contact")
def contact():
    return render_template("pages/contact.html")

@bp.route("/contact/contact_info")
def contact_info():
    # contact_info.html leads to a separate page
    return render_template("pages/contact_info.html")

