import json

from flask import Blueprint

from typing import Sequence

from models import URLDataSource

blueprint = Blueprint("StatusController", __name__)


def data_sources() -> Sequence[URLDataSource]:
    return []


@blueprint.route("/")
def index():
    sources = data_sources()
    if len(sources) == 0:
        return "[]"
    else:
        result = [model.check().__dict__() for model in sources]

        return json.dumps(result)
