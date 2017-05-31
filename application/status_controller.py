from flask import Blueprint

from typing import Callable, Sequence

blueprint = Blueprint("StatusController", __name__)


def data_sources() -> Sequence[Callable]:
    return []


@blueprint.route("/")
def index():
    sources = data_sources()
    if len(sources) == 0:
        return "Not yet configured"
    else:
        foo = [x() for x in sources]

        return str(foo)
