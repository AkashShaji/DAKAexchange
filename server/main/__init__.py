from flask import Flask, jsonify, request, g, make_response
from flask import url_for, redirect, flash, render_template

from flask import session as login_session

from server.main.models import Base, User, Transactions
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from functools import wraps

from server.main.models import User, Base
import random, string, urllib3, json, codecs, datetime
import flask_login
from flask_login import LoginManager, login_user

# from itsdangerous import URLSafeTimedSerializer

# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

#===================== INIT CODE ============================

engine = create_engine('sqlite:///site.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.secret_key = "userloginapplication"
app.debug = True

http = urllib3.PoolManager()
reader = codecs.getreader('utf-8')

# server = smtplib.SMTP('smtp.gmail.com', 587)

# ================= BEGIN LOGIN REQUIREMENT CODE ==============

@login_manager.user_loader
def load_user(user_id):
    '''
    Takes a unicode format user id and uses it to retrieve the respective user
    object to be used by the login_manager
    '''
    
    return session.query(User).filter_by(id=int(user_id)).first()

# ================== END LOGIN REQUIREMENT CODE ===============

@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/menu', methods=['GET', 'POST'])
def menu():
    # REQUEST URL:
    # https://www.dineoncampus.com/v1/location/menu.json?date=2018-01-13T03:00:59.764Z&location_id=5877ad223191a20074d827dc&platform=0&site_id=5751fd2b90975b60e0489294
    # mess with the 'date' parameter to get menu for specific days
    items = []

    if request.method == 'POST':
        date = str(request.form['date'])
        response = json.loads(http.request('GET', 'https://www.dineoncampus.com/v1/location/menu.json?date='+date+'T03:00:59.764Z&location_id=5877ad223191a20074d827dc&platform=0&site_id=5751fd2b90975b60e0489294').data)

        if response['status'] == "error" or not date:
            flash("Invalid entry")
            return redirect(url_for('menu'))

        parsed_date = date.split("-")

        for period in response['menu']['periods'][0:-1]:
            period_items = []
            for food_type in period['categories']:
                period_items.append([(food_type['name'] + " - " + food["name"]) for food in food_type['items']])

            items.append(period_items)

        return render_template('menu.html', breakfast=items[0], lunch=items[1], dinner=items[2], late_night=items[3], date=str(int(parsed_date[1]))+"/"+str(int(parsed_date[2])))
    else:
        current_date = datetime.date.today()
        response = json.loads(http.request('GET', 'https://www.dineoncampus.com/v1/location/menu.json?date='+str(current_date.year) + '-' + str(current_date.month) + '-' + str(current_date.day) +'T03:00:59.764Z&location_id=5877ad223191a20074d827dc&platform=0&site_id=5751fd2b90975b60e0489294').data)

        for period in response['menu']['periods'][0:-1]:
            period_items = []
            for food_type in period['categories']:
                period_items.append([(food_type['name'] + " - " + food["name"]) for food in food_type['items']])

            items.append(period_items)

        return render_template('menu.html', breakfast=items[0], lunch=items[1], dinner=items[2], late_night=items[3], date=str(current_date.month)+"/"+str(current_date.day))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        psk = request.form['password']

        if session.query(User).filter(User.email == email).count() == 0:
            flash("Wrong username or password")
            return redirect(url_for('login'))

        potential_user = session.query(User).filter(User.email == email).first()
        if potential_user.verify_password(psk):
            login_user(potential_user, force=True)
            potential_user.is_authenticated = True

            return redirect(url_for('view_profile', user_id=potential_user.id))
        else:
            flash("Wrong username or password")
            redirect(url_for('login'))
    else:
        return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        flask_login.logout_user()
        flash("Logout Successful")
        return redirect(url_for('index'))
    else:
        return render_template('logout.html')


@app.route('/')
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = request.form['name']
        email = request.form['email']
        password = request.form['pass']
        confirm = request.form['confirmpass']
        # confirm_code = generate_code()

        # check if user already exists
        if session.query(User).filter(User.email == email).count() > 0:
            flash("User already exists. Please login")
            return redirect(url_for('login'))

        elif password != confirm:
            flash("Passwords don't match")
            return redirect(url_for('signup'))

        newUser = User(name=user, email=email)
        newUser.hash_password(password)

        session.add(newUser)
        session.commit()

        login_user(newUser, force=True)
        newUser.is_authenticated = True

        flash("Welcome " + user + ". You have successfully signed up")

        # msg = MIMEMultipart()
        # msg['From'] = 'DoNotReply@teambuilder.com'
        # msg['To'] = email
        # msg['Subject'] = 'Email confirmation'
        # body = render_template('email.html', name=user, code=confirm_code)
        # msg.attach(MIMEText(body, 'html'))
        #
        # try:
        #     server.starttls()
        # except:
        #     while True:8
        #         try:
        #             server.connect()
        #             break
        #         except:
        #             pass
        #     server.starttls()
        #
        # server.login('fbar620@gmail.com', 'fake_password')
        # text = msg.as_string()
        # try:
        #     server.sendmail('DoNotReply@teambuilder.com', email, text)
        # except:
        #     flash("Invalid email")
        #     return jsonify(success=False, error="email")
        #
        # server.quit()

        return redirect(url_for('view_profile', user_id=newUser.id))
    else:
        return render_template('signup.html')


@app.route('/<user_id>/profile', methods=['GET', 'POST'])
def view_profile(user_id):

    if request.method == "POST":
        userID = request.form['user_id']

        # If the userID becomes invalid, push to a 404 page
        # Else

        return render_template('base.html', uID=userID)
    else:
        return render_template('profile.html')

# @app.route('/<user>/profile', methods=['GET', 'POST'])
# def view_profile(user):
#    return "This is where users can view their profile"


@app.route('/<user>/profile/edit', methods=['GET', 'POST'])
def edit_profile(user):
    return "This is where users can edit their profile"


@app.route('/<user>/requests_sent', methods=['GET', 'POST'])
def view_sent_requests(user):
    user_requests = session.query(Transactions).filter_by(client=user).all()
    return "This is where a user can see the requests they've sent to other users"


@app.route('/<user>/requests_received', methods=['GET', 'POST'])
def view_received_requests(user):
    user_requests = session.query(Transactions).filter_by(seller=user).all()
    return "This is where a user can see the requests they've received from other users"


@app.route("/search", methods=['GET', 'POST'])
def search():
    return "This is where search results will appear"


@app.route("/search/<selected_user>", methods=['GET', 'POST'])
def user_searched(selected_user):
    return "This is where information about the user clicked on from searching will appear"


@app.route("/search/<selected_user>/request", methods=['GET', 'POST'])
def request_user(selected_user):
    return "This is where users can request another user to sell to/buy from"


@app.route("/buy", methods=['GET', 'POST'])
def buy():
    if request.method == "POST":
        timeRaw = request.form['timeSearch']
        time = datetime.datetime.strptime(timeRaw, '%H:%M')

        sellers = session.query(User).filter(and_(User.start_time.time() <= time.time(), User.end_time.time() >= time.time())).all()
        sellers_data = []

        for seller in sellers:
            data = []

            data.append("Profile Picture")
            data.append(seller.name)
            data.append(seller.swipe_price)

            sellers_data.append(data)

        return render_template("buy.html", sellers=[], time=timeRaw)
    else:
        current_time = datetime.datetime.now()
        time = str(current_time.hour) + ":" + str(current_time.minute)
        return render_template("buy.html", sellers=[], time=time)