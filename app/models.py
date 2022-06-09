from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
from datetime import datetime
import jwt
from app.config import Config as cfg

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    password_hash = db.Column(db.String)
    is_email_validated = db.Column(db.Boolean)
    time_of_completed_task = db.Column(db.DateTime)
    tasks = db.relationship('Todo', back_populates='user')

    @property
    def password(self):
        raise Exception("No")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def name_exists(name):
        return User.query.filter(User.name == name).first()

    @staticmethod
    def email_exists(email):
        return User.query.filter(User.email == email).first()

    def get_token(self, expires_in=600):
        return jwt.encode({'usr': self.id, 'exp': time() + expires_in}, cfg.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def validate_token(token):
        try:
            id = jwt.decode(token, cfg.SECRET_KEY, algorithms=['HS256'])['usr']
        except:
            return
        return User.query.get(id)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String)
    is_daily = db.Column(db.Boolean)
    is_completed = db.Column(db.Boolean)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', back_populates='tasks')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


