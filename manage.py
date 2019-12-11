from flask_script import Manager
from flask import current_app
from app import create_app


def create_my_app():
    app = create_app()
    return app


APP = create_my_app()
manager = Manager(APP)


@manager.command
def run():
    port = int(current_app.config['PORT'])
    host = current_app.config['HOST']
    debug = current_app.config['DEBUG']
    current_app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    manager.run()
