from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ENUM

db = SQLAlchemy()

class NotificationsModel(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, nullable=False)
    n_type = db.Column(ENUM("like", "comment", "follow_request", name="NotificationType"))
    user_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime(100))

    def toJSON(self):
        return {
            "id": self.id,
            "n_type": self.n_type,
            "source_id": self.source_id
        }

    def __repr__(self) -> str:
        return f"Notification: {self.toJSON()}"