from flask1 import db, login_manager
from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import datetime, timezone
from flask_login import UserMixin


@login_manager.user_loader
def login_user(user_id):
    return db.session.get(User, int(user_id))

#creating a database this will ceate a database in our folder
class User(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file=db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(20),nullable=False)
    posts=db.relationship("Post", backref="author", lazy=True)

    def get_reset_token(self):
        s=Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({"user_id": self.id}, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token, expires=1800):
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id=s.loads(token, expires, salt='password-reset-salt')["user_id"]
        except:
            return None
        return db.session.get(User, user_id)


    def __repr__(self):
        return "user('{}','{}','{}')".format(self.username, self.email, self.password)
class Post(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(80), nullable=False)
    date_posted=db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    content=db.Column(db.Text, nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return "post('{}','{}', '{}')".format(self.title, self.date_posted, self.content)
