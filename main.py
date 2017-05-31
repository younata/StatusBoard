from flask import Flask
from os import getenv

import status_controller

app = Flask(__name__)
app.register_blueprint(status_controller.blueprint)
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:////tmp/test.db')

if __name__ == "__main__":
    app.run()
