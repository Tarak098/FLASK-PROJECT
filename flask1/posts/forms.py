from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class CreatePostForm(FlaskForm):
    title=StringField("Title", validators=[DataRequired()])
    content=TextAreaField("content", validators=[DataRequired()])
    submit=SubmitField("post")
