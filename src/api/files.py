from flask import request, send_from_directory, Blueprint, current_app
from werkzeug.utils import secure_filename

import os

from .auth import auth
from src.db.db import db
from src.utils import hashes, filenames, responses
from src.models.file import File


files = Blueprint("files", __name__)


@files.route("/upload", methods=["POST"])
@auth.login_required
def upload_file():
    if "file" not in request.files:
        return responses.no_file_attached()

    file = request.files["file"]
    if file.filename == "":
        return responses.no_file_err()

    hashed_file = hashes.file_hash(auth.current_user().username, file.read())
    file.seek(0)

    prev_file = File.query.filter(File.hashed_file == hashed_file).first()
    if prev_file:
        return responses.success_response(file.filename)

    file_dir = hashed_file[:2]
    origin_filename = secure_filename(file.filename)
    new_filename = filenames.collect_new_name(hashed_file, origin_filename)
    path = os.path.join(file_dir, new_filename)

    file_db = File(
        user_id=auth.current_user().id,
        filename=new_filename,
        hashed_file=hashed_file,
        path=path,
    )
    db.session.add(file_db)

    try:
        os.makedirs(
            os.path.join(current_app.config["UPLOAD_FOLDER"], file_dir), exist_ok=True
        )
        file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], path))
    except Exception as e:
        print(e)
        db.session.rollback()
        return responses.server_error("Unable to save file.")

    db.session.commit()

    return responses.success_upload(hashed_file)


@files.route("/delete", methods=["POST"])
@auth.login_required
def delete_file():
    if "file_hash" not in request.json:
        return responses.no_hash_err()

    file_hash = request.json["file_hash"]
    file = File.query.filter(File.hashed_file == file_hash).first()

    if not file:
        return responses.no_file_err(file_hash)

    if file.user_id != auth.current_user().id:
        return responses.forbidden_err(file_hash)

    db.session.delete(file)

    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file.path)
    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
            db.session.rollback()
            return responses.server_error("Unable to delete file.")

    db.session.commit()

    return responses.success_delete()


@files.route("/download/", methods=["GET"])
def download_file():
    file_hash = request.args.get("file_hash", None)

    if file_hash is None:
        return responses.no_hash_err()

    file = File.query.filter(File.hashed_file == file_hash).first()

    if not file:
        return responses.no_file_err(file_hash)

    dir_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file_hash[:2])

    if os.path.isfile(os.path.join(dir_path, file.filename)):
        return send_from_directory(os.path.join("../", dir_path), file.filename)

    return responses.no_file_err(file.filename)
