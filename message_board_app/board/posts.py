from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from .models import Posts
from .extensions import db

bp = Blueprint("posts", __name__)

@bp.route("/create", methods=("GET", "POST")) # GET: Used to display the form to create a post. POST: Used to submit the form and create a new post on the server.
def create():
    if request.method == "POST":
        
        # get data from form
        author = request.form["author"]
        message = request.form["message"]

        if author and message:
            # create a new post instance
            new_post = Posts(author=author, message=message)

            # Add and commit the new post to the database
            db.session.add(new_post)
            db.session.commit()

            # close connection, not necessary with SQLAlchemy
            # db.session.close()

            # log new post
            current_app.logger.info(f"New post by {author}")

            # calling flash method to display success message
            flash(f"Thanks for posting, {author}!", category="success")

            # redirect to posts page
            return redirect(url_for("posts.posts"))
        
        else:
            # display error message
            flash("All fields required", "error")
            # return render_template("posts/create.html", error="All fields required")

    return render_template("posts/create.html")

@bp.route("/posts")
def posts():

    # Query the database for all posts
    posts = Posts.query.all()  # This fetch all posts from database as a list of Post objects

    return render_template("posts/posts.html", posts=posts)