import os


class Config:
    SECRET_KEY = 'b384e5964d98834d082dc208c8140f43'
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USERNAME = os.environ.get("EMAIL_USER")
    MAIL_PASSWORD = "knbm xcee rrzh gtyu"
