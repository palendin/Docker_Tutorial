# this will create a message board utilizing the following concept: application factory, blueprint, view functions (navigation menu)
# reference: https://realpython.com/flask-project/#leverage-blueprints
from flask import Flask
import os
from . import posts, pages, errors
from dotenv import load_dotenv # load .env file
from sqlalchemy import text
from .extensions import db
import logging

# load .env file
load_dotenv()

# this function is "application factory", allows to flexibility and scaling
def create_app():

    # start the flask instance
    app = Flask(__name__)

    # Configure logging to file
    logging.basicConfig(filename='app.log', level=logging.DEBUG)

    # Log a message
    app.logger.debug("Debugging information at app start...")

    # enabling the use of environment variables, assess to all variables with "Flask_"
    app.config.from_prefixed_env()

    # get Flask from Environment
    app.config["ENVIRONMENT"] = os.getenv("ENVIRONMENT")

    # get Database from Environment, must be defined before db.init_app(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")

    # initiate database
    db.init_app(app)

    # Create tables if they don't exist
    with app.app_context():
        try:
            with db.engine.begin() as connection: # begin() automatically manages the transaction, which often resolves issues like schema creation errors by ensuring everything runs within a properly handled transaction context
                app.logger.debug('Creating schema')
                connection.execute(text("CREATE SCHEMA IF NOT EXISTS message_board"))
                app.logger.debug('Schema created or already exists')
                
            
            app.logger.debug('Creating tables')
            db.create_all()
            app.logger.debug('Tables created or already exist')

        except Exception as e:
            app.logger.error(f"Error creating schema or tables: {e}")

    # register blueprints, must be after initiating the database and creating the tables
    app.register_blueprint(pages.bp)
    app.register_blueprint(posts.bp)
    app.register_error_handler(404, errors.page_not_found)

    # adding logging to receive information about the server
    #print(f"Current Environment: {os.getenv('ENVIRONMENT')}") # method for getting variable that doesnt start with "FLASK_"
    #print(f"Using Database: {app.config.get('DATABASE')}") # method for getting variable that starts with "FLASK_"
    app.logger.debug(f"Current Environment: {os.getenv('ENVIRONMENT')}")
    app.logger.debug(f"Using Database: {os.getenv('SQLALCHEMY_DATABASE_URI')}")

    return app




