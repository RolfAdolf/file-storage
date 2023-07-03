from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

from src.models.user import User


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username: str, password: str):
    user = User.query.filter_by(username=username).first()
    if not user:
        return False

    if check_password_hash(user.hashed_password, password):
        return user

    return False


def create_superuser(
    db: object,
    username: str,
    password: str,
) -> None:
    user = User.query.filter_by(username=username).first()
    if user:
        if check_password_hash(user.hashed_password, password):
            return
        else:
            db.session.delete(user)
            db.session.flush()

    new_user = User(username=username, hashed_password=generate_password_hash(password))
    db.session.add(new_user)

    db.session.commit()
