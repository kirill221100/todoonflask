from flask import render_template
from flask_mail import Message
from app.config import Config as cfg
from app import app, mail
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

def send_validation_email(user):
    token = user.get_token()
    send_email('[Todo] Validate your email',
               sender=cfg.MAIL_USERNAME,
               recipients=[user.email],
               text_body=render_template('validate.txt', token=token),
               html_body=render_template('validate.html', token=token))
