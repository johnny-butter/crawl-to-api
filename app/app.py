import os
from flask import Flask
from app.controllers.rent import bp_rent
from config.config import get_config

__all__ = ['create_app']


def create_app():
    app_name = 'rent591'
    app = Flask(app_name, instance_relative_config=True)
    env = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(get_config(env))
    app.register_blueprint(bp_rent)

    return app
