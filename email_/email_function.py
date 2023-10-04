import os
from email.mime.text import MIMEText
from smtplib import SMTP_SSL


template_path = 'email_template.html'


def load_email_template(file_path: str) -> str:
    with open(file_path, 'r') as file:
        content = file.read()
    return content


def send_email(email: str, username: str):
    email_template = load_email_template(template_path)

    msg = MIMEText(email_template.replace("[USERNAME]", username), "html")
    msg['Subject'] = "Welcome to NoteApp!"
    msg['From'] = os.getenv("OWN_EMAIL")
    msg['To'] = email

    server = SMTP_SSL("mail.privateemail.com", 465)
    server.login(os.getenv("OWN_EMAIL"), os.getenv("OWN_EMAIL_PASSWORD"))

    server.send_message(msg)
    server.quit()
