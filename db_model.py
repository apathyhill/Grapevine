import hashlib
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class DB_User(db.Model):
    __tablename__ = "User"

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(20), unique=True, nullable=False)
    display_name  = db.Column(db.String(32), nullable=False)
    password_hash = db.Column(db.LargeBinary(), nullable=False)
    email         = db.Column(db.String(), unique=True, nullable=False)
    session_key   = db.Column(db.String(16))

    def to_json(self):
        return {
            "id":           self.id,
            "username":     self.username,
            "display_name": self.display_name,
            "avatar_url":   f"https://www.gravatar.com/avatar/{hashlib.md5(self.email.lower().encode()).hexdigest()}.jpg"
        }


class DB_Post(db.Model):
    __tablename__ = "Post"

    id        = db.Column(db.Integer, primary_key=True)
    text      = db.Column(db.Unicode(256), nullable=False)
    author_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_json(self):
        result = {
            "id": self.id,
            "text": self.text,
            "timestamp": self.timestamp
        }

        author = DB_User.query.filter_by(id=self.author_id).first()
        if author:
            result["author"] = author.to_json()

        return result


if __name__ == "__main__":
    db.create_all()