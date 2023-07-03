from src.db.db import db


class File(db.Model):
    __tablename__ = "file"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    filename = db.Column(db.String)
    hashed_file = db.Column(db.String, index=True, unique=True)
    path = db.Column(db.String)

    def __repr__(self):
        return f"<File-{self.id}>"
