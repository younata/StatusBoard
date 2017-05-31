import requests
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class CheckResult(object):
    def __init__(self, url: str, success: bool):
        self.url = url
        self.success = success

    def __eq__(self, o: object) -> bool:
        if self is o:
            return True
        elif type(self) != type(o):
            return False
        return self.url == o.url and self.success == o.success

    def __repr__(self) -> str:
        return '<CheckResult url="%r" success="%r" />' % (self.url, self.success)

    def __dict__(self) -> dict:
        return {'url': self.url, 'success': self.success}


class URLDataSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, unique=True)

    def __init__(self, url: str):
        self.url = url

    def check(self) -> CheckResult:
        result = requests.get(self.url)
        success = False
        if result.status_code == 200:
            success = True
        return CheckResult(self.url, success)
