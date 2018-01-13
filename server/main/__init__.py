from flask import Flask, jsonify, request, g, make_response
from flask import url_for, redirect, flash, render_template

from flask import session as login_session

from main.models import Base, User, PendingUser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from functools import wraps

import random, string

import flask_login
from flask_login import LoginManager, login_user

# from itsdangerous import URLSafeTimedSerializer

# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

#===================== INIT CODE ============================

engine = create_engine('postgresql://localhost:8000/site.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.secret_key = "userloginapplication"
app.debug = True

# server = smtplib.SMTP('smtp.gmail.com', 587)

# ================= BEGIN LOGIN REQUIREMENT CODE ==============

@login_manager.user_loader
def load_user(user_id):
    '''
    Takes a unicode format user id and uses it to retrieve the respective user
    object to be used by the login_manager
    '''
    user = session.query(User).filter_by(id=int(user_id)).first()
    return user

# ================== END LOGIN REQUIREMENT CODE ===============

@app.route('/')
@app.route('/index')
def index():
    return "This is a test"
