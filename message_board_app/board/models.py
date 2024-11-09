from .extensions import db  # Importing the db instance from __init__.py
from datetime import datetime

# model for posts - make sure to use SQLAlchemy to interact with the database in the view files (see posts.py)
class Posts(db.Model):
    __tablename__ = 'posts'

    __table_args__ = {'schema': 'message_board'}  # specify the schema

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author = db.Column(db.String(50), unique=True, nullable=False)
    message = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, default=datetime.now())  # Automatically set to current time when created


class User(db.Model):
    __tablename__ = 'logins'

    __table_args__ = {'schema': 'user_info'}  # specify the schema

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    # def __repr__(self):
    #     return f'<User {self.username}>'
