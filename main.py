from flask import Flask
from os import getenv

import status_controller

app = Flask(__name__)
app.register_blueprint(status_controller.blueprint, url_prefix='/status')
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:////tmp/test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route("/")
def index():
    return "welcome"

if __name__ == "__main__":
    app.run()
