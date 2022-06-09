from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate
from app.models import db
from app.config import Config
from flask_apscheduler import APScheduler

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)
scheduler = APScheduler()
scheduler.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

from app.views import *