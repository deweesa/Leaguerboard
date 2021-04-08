import os

from flask import (Flask, render_template)
from flask_sqlalchemy import SQLAlchemy


database = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    db_user = str(os.getenv('DB_USER'))
    db_password = str( os.getenv('DB_PASSWORD'))
    db_host = str(os.getenv('DB_HOST'))
    db_port = str(os.getenv('DB_PORT'))
    db_name = str(os.getenv('DB_NAME'))

    app.config.from_mapping(
        SECRET_KEY='dev',
        #DATABASE=os.path.join(app.instance_path, 'Leaguerboard.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')#.replace("://", "ql://", 1),
    )

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
