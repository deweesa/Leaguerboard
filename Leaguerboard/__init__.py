import os

from flask import (Flask, render_template)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.getenv('DATABASE_URL')
    )

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
