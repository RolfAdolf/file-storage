from flask_testing import TestCase
from flask import url_for
from werkzeug.security import generate_password_hash
from requests.auth import _basic_auth_str
from werkzeug.datastructures import FileStorage

from pathlib import Path
import shutil
import os
import json

from src.app import create_app
from src.db.db import db
from src.models import user, file
from src.utils.hashes import generate_random_string
from src.utils.filenames import collect_new_name


test_media_samples = Path("./samples/")

test_files = (
    ("file_example_JPEG_4MB.jpeg", "image/jpeg"),
    ("file_example_MP3_5MG.mp3", "audio/mpeg"),
    ("file_example_PDF_15MB.pdf", "application/pdf"),
    ("file_example_PNG_3MB.png", "image/png"),
    ("file_example_WAV_10MG.wav", "audio/x-wav"),
)

test_user = {
    "username": generate_random_string(),
    "password": generate_random_string(),
}


class Base(TestCase):
    def create_app(self):
        # Set the test configuration
        app = create_app(
            {
                "SQLALCHEMY_DATABASE_URI": "sqlite://",
                "TESTING": True,
                "ADMIN_USERNAME": test_user["username"],
                "ADMIN_PASSWORD": test_user["password"],
            }
        )

        # Temporary test directory
        test_dir = Path(app.root_path).parent / "test_storage"
        self.test_dir = test_dir
        app.config["UPLOAD_FOLDER"] = str(test_dir)

        return app

    def setUp(self) -> None:
        self.auth_header = _basic_auth_str(test_user["username"], test_user["password"])

    def tearDown(self) -> None:
        # Remove all test directories and files
        shutil.rmtree(self.app.config["UPLOAD_FOLDER"], ignore_errors=True)

        db.session.remove()
        db.drop_all()


class UploadAPITests(Base):
    def test_upload_status(self):
        """Upload 5 test files and check the
        test storage directory.
        """
        for test_file in test_files:
            with open(test_media_samples / test_file[0], "rb") as f:
                post_file = FileStorage(
                    stream=f,
                    filename=test_file[0],
                    content_type=test_file[1],
                )
                response = self.client.post(
                    url_for("files.upload_file"),
                    data={
                        "file": post_file,
                    },
                    content_type="multipart/form-data",
                    headers={"Authorization": self.auth_header},
                )
            self.assertEqual(response.status_code, 200)

        db_files = file.File.query.all()
        self.assertEqual(len(db_files), 5)

        for uploaded_file in db_files:
            if not os.path.isfile(
                os.path.join(self.app.config["UPLOAD_FOLDER"], uploaded_file.path)
            ):
                self.assertFalse(
                    True,
                    msg=f"There is no file {uploaded_file.filename} in {self.test_dir}",
                )

    def test_no_file_upload(self):
        """Invalid request body."""
        response = self.client.post(
            url_for("files.upload_file"),
            content_type="multipart/form-data",
            headers={"Authorization": self.auth_header},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Error", response.json)


class DeleteAPITests(Base):
    def setUp(self) -> None:
        """Create 5 records in database."""
        super().setUp()

        for test_file in test_files:
            hashed_file = generate_random_string()

            filepath = Path(hashed_file[:2]) / collect_new_name(
                hashed_file, test_file[0]
            )
            (self.test_dir / filepath.parent).mkdir(exist_ok=True, parents=True)
            shutil.copy(
                test_media_samples / test_file[0],
                self.test_dir / filepath,
            )

            new_file = file.File(
                user_id=1,
                filename=filepath.name,
                hashed_file=hashed_file,
                path=str(filepath),
            )
            db.session.add(new_file)

        db.session.commit()

    def test_valid_delete(self):
        """Delete five files from storage and database."""
        db_files = file.File.query.all()

        for db_file in db_files:
            response = self.client.post(
                url_for("files.delete_file"),
                data=json.dumps(
                    {
                        "file_hash": db_file.hashed_file,
                    }
                ),
                content_type="application/json",
                headers={"Authorization": self.auth_header},
            )
            self.assertEqual(response.status_code, 204)

            if os.path.isfile(self.test_dir / db_file.path):
                self.assertFalse(True, msg=f"File {db_file.filename} was not deleted")

    def test_not_valid_delete(self):
        """Invalid body request."""
        response = self.client.post(
            url_for("files.delete_file"),
            data=json.dumps(
                {
                    "file_hash": generate_random_string(),
                }
            ),
            content_type="application/json",
            headers={"Authorization": self.auth_header},
        )
        self.assertEqual(response.status_code, 400)


class DownloadAPITests(Base):
    def setUp(self) -> None:
        """Create one test record in database."""
        hashed_file = generate_random_string()

        filepath = Path(hashed_file[:2]) / collect_new_name(
            hashed_file, test_files[0][0]
        )
        (self.test_dir / filepath.parent).mkdir(exist_ok=True, parents=True)
        shutil.copy(
            test_media_samples / test_files[0][0],
            self.test_dir / filepath,
        )

        new_file = file.File(
            user_id=1,
            filename=filepath.name,
            hashed_file=hashed_file,
            path=str(filepath),
        )
        db.session.add(new_file)

        db.session.commit()

    def test_download(self):
        db_file = file.File.query.all()[0]

        response = self.client.get(
            url_for("files.download_file", file_hash=db_file.hashed_file),
        )
        self.assertEqual(response.status_code, 200)
        response.close()

    def test_not_valid_download(self):
        response = self.client.get(
            url_for("files.download_file", file_hash=generate_random_string()),
        )
        self.assertEqual(response.status_code, 400)
