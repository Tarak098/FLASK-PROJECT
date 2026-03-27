from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from flask1.models import User

class RegistrationForm(FlaskForm):
    username=StringField("username", validators=[DataRequired(), Length(min=2, max=20)])
    email=StringField("email", validators=[DataRequired(), Email()])
    password=PasswordField("password", validators=[DataRequired(), Length(min=8)])
    confirm_password=PasswordField("confirm password", validators=[DataRequired(), EqualTo("password")])
    submit=SubmitField("sign up")

    def validate_username(self, username):
        user=User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("username already exist")
    def validate_email(self, email):
        user=User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("email already exist")


class LoginForm(FlaskForm):
    email=StringField("email", validators=[DataRequired(), Email()])
    password=PasswordField("password", validators=[DataRequired()])
    remember=BooleanField("Remember me")
    submit=SubmitField("login")

class UpdateAccountForm(FlaskForm):
    username=StringField("username", validators=[DataRequired(), Length(min=2, max=20)])
    email=StringField("email", validators=[DataRequired(), Email()])
    picture=FileField("update profile picture", validators=[FileAllowed(["jpg", "png"])])
    submit=SubmitField("Update")
    def validate_username(self, username):
        if username.data != current_user.username:
            user=User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("username already exist")
    def validate_email(self, email):
        if email.data != current_user.email:
            user=User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("email already exist please choose different one")


class RequestResetForm(FlaskForm):
    email = StringField("email", validators=[DataRequired(), Email()])
    submit=SubmitField("Request Password Reset")

    def validate_email(self, email):
        user=User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("No account with that email! you must register first.")



class ResetPasswordForm(FlaskForm):
    password = PasswordField("password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("confirm password", validators=[DataRequired(), EqualTo("password")])
    submit=SubmitField("Reset Password")
