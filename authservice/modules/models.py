from flask_praetorian import Praetorian
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
guard = Praetorian()

class AuthModel(db.Model):
    # Holds basic user info: username, password, first name, last
    # name, email
    __tablename__ = "auth"

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    _password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime(100), nullable=False)

    
    @property
    def password(self):
        return self._password

    @property
    def identity(self):
        return self.id

    @property
    def rolenames(self):
        try:
            return self.roles.split(",")
        except:
            return []

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @password.setter
    def password(self, password):
        self._password = guard.hash_password(password)

    def verify_password(self, username, password):
        return guard.authenticate(username, password)

    def toJSON(self):
        return {
            "user_id": self.id,
            "username": self.username,
            "email": self.email
        }

    def __repr__(self) -> str:
        return f"User: {self.id}"