from src.db.db import db


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, index=True)
    hashed_password = db.Column(db.String)

    files = db.relationship("File", cascade="all,delete-orphan", backref="user")

    def __repr__(self):
        return f"User-{self.id}"
