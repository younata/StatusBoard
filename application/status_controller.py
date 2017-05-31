from functools import wraps

from flask import Blueprint, jsonify, request, Response

from typing import Sequence

from models import URLDataSource, db

blueprint = Blueprint("StatusController", __name__)


def data_sources() -> Sequence[URLDataSource]:
    return []


def authenticator(username: str, password: str) -> bool:
    return False


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_authentication(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not authenticator(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


@blueprint.route("/")
def index():
    result = [model.check().__dict__() for model in data_sources()]

    return jsonify(result)


@blueprint.route("/create", methods=["POST"])
@requires_authentication
def create():
    content = request.get_json()
    if content is None:
        return jsonify({"error": "JSON Required"}), 400
    url = content.get("url")
    if type(url) is str:
        if URLDataSource.query.filter_by(url=url).first() is not None:
            return jsonify({"error": "Exists"}), 400
        data_source = URLDataSource(url)
        db.session.add(data_source)
        db.session.commit()
        return jsonify({}), 201
    return jsonify({"error": "URL Required"}), 400
