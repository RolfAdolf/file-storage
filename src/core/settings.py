from os import environ


# Database config
POSTGRES_HOST = environ.get("POSTGRES_HOST")
POSTGRES_PORT = environ.get("POSTGRES_PORT")
POSTGRES_DB = environ.get("POSTGRES_DB")
POSTGRES_USER = environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD")

SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Storage config
UPLOAD_FOLDER = environ.get("UPLOAD_FOLDER")
MAX_CONTENT_LENGTH = int(environ.get("MAX_CONTENT_LENGTH"))

# Default user config
ADMIN_USERNAME = environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = environ.get("ADMIN_PASSWORD")


SECRET_KEY = environ.get("SECRET_KEY")
