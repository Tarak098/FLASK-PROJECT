import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "b384e5964d98834d082dc208c8140f43")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///site.db"
    MAIL_SERVER = os.environ.get("MAIL_SERVER") or os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)
    MAIL_USERNAME = os.environ.get("EMAIL_USER") or os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("EMAIL_PASS") or os.environ.get("MAIL_PASSWORD")

