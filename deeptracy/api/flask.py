from flask import Flask
from flask_cors import CORS

from deeptracy.api.project_blueprint import project


def setup_api():
    flask_app = Flask('deeptracy_api')
    CORS(flask_app)

    load_blueprints(flask_app)

    return flask_app


def load_blueprints(flask_app):
    # Register blueprints
    root = '/api/'
    prev1 = root + '1'

    flask_app.register_blueprint(project, url_prefix=prev1 + '/project')
    # flask_app.register_blueprint(language, url_prefix=prev1 + '/language')
    # flask_app.register_blueprint(project, url_prefix=prev1 + '/project')
    # flask_app.register_blueprint(result, url_prefix=prev1 + '/result')
