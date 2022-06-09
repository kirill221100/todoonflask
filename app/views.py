from flask import render_template, request, redirect, url_for, session, flash
from app import app, db, scheduler
from app.models import User, Todo
from app.email import send_validation_email, send_email
from app.config import Config as cfg
from datetime import datetime

@scheduler.task('interval', id='do_job_1', seconds=86400)
def job1():
    with app.app_context():
        for user in db.session.query(User).filter(User.is_email_validated == True).all():
            if (datetime.utcnow() - user.time_of_completed_task).seconds >= 86400:
                send_email('[Todo] Mention',
                           sender=cfg.MAIL_USERNAME,
                           recipients=[user.email],
                           text_body=render_template('remember.txt'),
                           html_body=render_template('remember.html'))
scheduler.start()

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('name'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        user = db.session.query(User).filter(User.name==session['name']).first()
        task = Todo(task=request.form['task'], user=user, is_completed=False)
        if request.form.get('daily'):
            task.is_daily = True
        db.session.add(task)
        db.session.commit()
    return render_template('index.html', user=db.session.query(User).filter(User.name==session['name']).first())

@app.route('/completed/<int:id>')
def completed(id):
    if not session.get('name'):
        return redirect(url_for('login'))

    task = db.session.query(Todo).filter(Todo.id == id).first()
    task.user.time_of_completed_task = datetime.utcnow()
    if task.is_daily:
        task.is_completed = True
    else:
        db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    if not session.get('name'):
        return redirect(url_for('login'))

    task = db.session.query(Todo).filter(Todo.id == id).first()
    task.user.time_of_completed_task = datetime.utcnow()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('name'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        if not db.session.query(User).filter(User.name == request.form['name']).first().validate_password(request.form['password']):
            flash("Name or password are incorrect")
            return redirect(url_for('login'))
        session['name'] = request.form['name']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('name'):
        return redirect(url_for('index'))
    if request.method == "POST":
        if User.name_exists(request.form['name']):
            flash('This name is registered')
            return redirect(url_for('register'))

        if User.email_exists(request.form['email']):
            flash('This email is used')
            return redirect(url_for('register'))

        user = User(name=request.form['name'], password=request.form['password'], email=request.form['email'])
        session['name'] = request.form['name']

        db.session.add(user)
        db.session.commit()
        send_validation_email(user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    if not session.get('name'):
        return redirect(url_for('login'))
    session.pop('name')
    return redirect(url_for('login'))

@app.route('/validate/<string:token>')
def validate(token):
    user = User.validate_token(token)
    if not user:
        return redirect(url_for('index'))
    user.is_email_validated = True
    db.session.commit()
    return redirect(url_for('index'))

# @app.route('/change/<string:name>')
# def change(name):
#     user = db.session.query(User).filter(User.name == name).first()
#     user.email = 'asd'
#     db.session.commit()
#     return redirect(url_for('register'))