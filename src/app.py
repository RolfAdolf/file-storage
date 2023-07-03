from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv

from typing import Optional
from pathlib import Path
import os

from src.db.db import db_init, db
from src.api import files, auth


def create_app(test_config: Optional[os.PathLike] = None):
    app_ = Flask(__name__)

    # Set the environment variables from .env-file
    path_to_env = Path(app_.root_path).parent / ".env"
    load_dotenv(str(path_to_env))

    # Special configuration for tests
    if test_config is not None:
        app_.config.from_mapping(test_config)
    else:
        app_.config.from_pyfile(os.path.join(app_.root_path, "core/settings.py"))

    # Database initialization
    migrate = Migrate(app_, db)
    db_init(app_)
    with app_.app_context():
        auth.create_superuser(
            db,
            username=app_.config["ADMIN_USERNAME"],
            password=app_.config["ADMIN_PASSWORD"],
        )

    # File routes (/upload, /delete, /download)
    app_.register_blueprint(files.files, url_prefix="/")

    return app_


app = create_app()
