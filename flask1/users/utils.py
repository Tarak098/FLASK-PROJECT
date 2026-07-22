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
    if current_user.image_file and current_user.image_file != 'default.jpg':
        old_picture_path=os.path.join(current_app.root_path, "static/profile_pics", current_user.image_file)
        if os.path.exists(old_picture_path):
            os.remove(old_picture_path)
    return picture_fn



import requests

def send_reset_email(user):
    try:
        token = user.get_reset_token()
        reset_url = url_for("users.reset_password", token=token, _external=True)
        
        mail_user = current_app.config.get("MAIL_USERNAME") or os.environ.get("EMAIL_USER") or os.environ.get("MAIL_USERNAME")
        mail_pass = current_app.config.get("MAIL_PASSWORD") or os.environ.get("EMAIL_PASS") or os.environ.get("MAIL_PASSWORD")
        
        if not mail_user or not mail_pass:
            print(f"[Email Log Error] EMAIL_USER={mail_user}, EMAIL_PASS_SET={bool(mail_pass)}. Missing credentials.")
            return False

        clean_pass = mail_pass.strip()
        print(f"[Email Diagnostics] Sending email via user='{mail_user}', pass_prefix='{clean_pass[:8]}...', pass_len={len(clean_pass)}")

        # 1. Try Brevo HTTP API over Port 443 (Never blocked by Render firewall)
        if clean_pass.startswith("xsmtpsib-") or clean_pass.startswith("xkeysib-") or "brevo" in str(current_app.config.get("MAIL_SERVER", "")).lower() or len(clean_pass) > 50:
            url = "https://api.brevo.com/v3/smtp/email"
            payload = {
                "sender": {"email": mail_user, "name": "Flask Blog"},
                "to": [{"email": user.email}],
                "subject": "Password Reset Request",
                "htmlContent": f"""<p>To reset your password, click the link below:</p>
<p><a href="{reset_url}">{reset_url}</a></p>
<p>If you did not make this request, please ignore this email.</p>
<p><small style="color: #6c757d;">Note: If you don't see this email in your Inbox, please check your Spam, Junk, or Trash folder.</small></p>"""
            }
            headers = {
                "accept": "application/json",
                "api-key": clean_pass,
                "content-type": "application/json"
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            print(f"[Brevo API Response] Status {resp.status_code}: {resp.text}")
            if resp.status_code in [200, 201, 202]:
                return True
            else:
                print(f"[Brevo API Warning] Status {resp.status_code}: {resp.text}. Trying SMTP fallback...")

        # 2. Fallback to standard SMTP for local testing
        msg = MIMEText(f"""To reset your password, click the following link:
{reset_url}

If you did not make this request, simply ignore this email and no changes will be made.
""")
        msg["Subject"] = "Password Reset Request"
        msg["From"] = mail_user
        msg["To"] = f"{user.email}"

        mail_server = current_app.config.get("MAIL_SERVER", "smtp-relay.brevo.com")
        mail_port = int(current_app.config.get("MAIL_PORT", 587))

        if mail_port == 465:
            server = smtplib.SMTP_SSL(mail_server, 465, timeout=10)
            server.login(mail_user, clean_pass)
        else:
            try:
                server = smtplib.SMTP(mail_server, mail_port, timeout=10)
                server.starttls()
                server.login(mail_user, clean_pass)
            except Exception as e1:
                print(f"[SMTP Warning] STARTTLS port {mail_port} failed: {e1}. Trying SSL port 465...")
                server = smtplib.SMTP_SSL(mail_server, 465, timeout=10)
                server.login(mail_user, clean_pass)

        server.sendmail(mail_user, [user.email], msg.as_string())
        server.quit()
        print(f"[SMTP Success] Password reset email sent to {user.email}")
        return True
    except Exception as e:
        print(f"[Email Error] Failed to send password reset email: {e}")
        return False
