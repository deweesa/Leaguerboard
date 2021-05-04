"""This is the entry point for the Leaguerboard web app.

This is a project to learn more about Flask, Python, HTML, CSS, Heroku, etc.
The aim of this webapp is to be a op.gg/mobafire clone for use in a small 
discord group. Currently their is a rough prototype up on leagueboard.heroku.com
"""
import os

from flask import (Flask, render_template)
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap


database = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

    # If the app is being ran on heroku, their listed postgresql dialect is 
    # outdated, so we have to edit it a tad before handing it off to the app.
    if os.getenv('ENV') == 'heroku':
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("://", "ql://", 1)

    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    )

    Bootstrap(app)

    from . import models

    database.init_app(app)
    with app.app_context():
        database.create_all()

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    from . import db
    db.init_app(app)

    from . import summoner
    app.register_blueprint(summoner.bp)

    from . import team
    app.register_blueprint(team.bp)

    from . import champion
    app.register_blueprint(champion.bp)

    @app.route('/')
    def home():
        return render_template('home/home.html')

    """
    from . import filters
    @app.template_filter('readable')
    def readable(value):
        return filters.readable(value)

    @app.template_filter('queue')
    def queue(value):
        return filters.queue(value)
        """

    return app
