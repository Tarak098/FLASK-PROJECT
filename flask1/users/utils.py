import os
import secrets
from PIL import Image
from flask import url_for, current_app
import smtplib
from email.mime.text import MIMEText
from flask1 import mail
from flask_login import current_user
from flask1.config import Config


def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    _,f_ext=os.path.splitext(form_picture.filename)
    picture_fn=random_hex+f_ext
    picture_path=os.path.join(current_app.root_path, "static/profile_pics", picture_fn)

    outpu_size=(125,125)
    i=Image.open(form_picture)
    i.thumbnail(outpu_size)

    i.save(picture_path)
    if current_user.image_file:
        old_picture_path=os.path.join(current_app.root_path, "static/profile_pics", current_user.image_file)
        if os.path.exists(old_picture_path):
            os.remove(old_picture_path)
    return picture_fn



def send_reset_email(user):
    token=user.get_reset_token()
    msg = MIMEText(f"""To reset your password click the following link:
{url_for("users.reset_password", token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made
""")
    msg["Subject"] = "Password Reset Request"
    msg["From"] = current_app.config["MAIL_USERNAME"]
    msg["To"] = f"{user.email}"

    server = smtplib.SMTP(current_app.config["MAIL_SERVER"], current_app.config["MAIL_PORT"])
    server.starttls()
    server.login(current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"])
    server.sendmail(current_app.config["MAIL_USERNAME"], f"{user.email}", msg.as_string())
    server.quit()
