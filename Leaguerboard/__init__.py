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
    
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        #the below line is legacy from when sqlite3 was used to store data.
        #DATABASE=os.path.join(app.instance_path, 'Leaguerboard.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False,

        # FIXME: Need to have this configure dynamically depending on running
        # environment. 
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')#.replace("://", "ql://", 1),
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

    return app
