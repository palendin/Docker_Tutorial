# By setting up db in extensions.py, you can import and use it consistently throughout your app. 
# This setup ensures that your database session is properly managed and minimizes the risk of circular import errors

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()