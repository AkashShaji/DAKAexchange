import requests
from flask import Flask, jsonify, request, g, make_response, send_from_directory
from flask import url_for, redirect, flash, render_template

from flask import session as login_session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from functools import wraps

from main.models import Base, User, Transactions
import random, string, urllib3, json, codecs, datetime, os

import flask_login
from flask_login import LoginManager, login_user

from werkzeug.utils import secure_filename
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

UPLOAD_FOLDER = './static/profile_images'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

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

# def get_profile_image(user):
#     return send_from_directory(UPLOAD_FOLDER, user.profile_pic)

@app.route('/<user_id>/profile', methods=['GET', 'POST'])
def view_profile(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    is_seller = session.query(Transactions).filter_by(seller=user).all()
    # is_involved = session.query(Transactions).filter(Transactions.seller == user, Transactions.client != None).all()
    is_involved = session.query(Transactions).filter(Transactions.client == user).all()

    try:
        stime = user.start_time.strftime("%I:%M %p")
    except:
        stime = None

    try:
        etime = user.end_time.strftime("%I:%M %p")
    except:
        etime = None

    print(len(is_seller))
    print(len(is_involved))

    return render_template('profile.html', user=user, stime=stime, etime=etime, seller=is_seller, involved=is_involved) #, image=user.profile_pic

# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/<user_id>/profile/edit', methods=['GET', 'POST'])
def edit_profile(user_id):
    user = session.query(User).filter_by(id=user_id).first()

    if request.method == 'POST':
        new_name = request.form['new_name']
        new_email = request.form['new_email']


        new_swipes = request.form['new_swipes']
        new_price = request.form['new_price']

        if request.form['new_name'] == "":
            new_name = user.name
        if request.form['new_email'] == "":
            new_email = user.email

        if request.form['new_start'] == "":
            new_start = user.start_time
        else:
            stime_str = request.form['new_start']
            new_start = datetime.datetime.strptime(stime_str, '%H:%M')
        if request.form['new_end'] == "":
            new_end = user.end_time
        else:
            etime_str = request.form['new_end']
            new_end = datetime.datetime.strptime(etime_str, '%H:%M')

        if not request.form['new_swipes']:
            new_swipes = user.swipe_count
        if not request.form['new_price']:
            new_price = user.swipe_price
        # if 'new_pic' not in request.files:
        #     new_pic = user.profile_pic
        # else:
        #     file_in = request.files['new_pic']
        #     if file_in.filename == "" or not allowed_file(file_in.filename):
        #         new_pic = user.profile_pic
        #     else:
        #         filename = secure_filename(file_in.filename)
        #         new_pic = os.path.join(UPLOAD_FOLDER, filename)
        #         file_in.save(new_pic)

        user.name = new_name
        user.email = new_email
        # user.profile_pic = new_pic
        user.start_time = new_start
        user.end_time = new_end
        user.swipe_count = new_swipes
        user.swipe_price = new_price

        session.add(user)
        session.commit()

        return redirect(url_for('view_profile', user_id=user_id, stime=new_start.strftime("%I:%M %p"), etime=new_end.strftime("%I:%M %p")))
    else:
        return render_template('edit_profile.html', user_id=user_id)

@app.route('/<user_id>/profile/password', methods=['POST'])
def change_password(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    if request.method == 'POST':
        old_pass = request.form['old_pass']
        new_pass = request.form['new_pass']
        confirm_new = request.form['confirm_new']

        if user.verify_password(old_pass) and new_pass == confirm_new:
            user.hash_password(new_pass)
            session.add(user)
            session.commit()
        else:
            flash("Incorrect Credentials")

        return redirect(url_for('view_profile', user_id=user_id))

@app.route('/<transaction_id>/accept_request', methods=['GET'])
def accept_request(transaction_id):
    transaction = session.query(Transactions).filter_by(id=transaction_id).first()
    transaction.accepted_status = True

    session.add(transaction)
    session.commit()

    return redirect(url_for('index'))


@app.route('/<transaction_id>/redeem_swipe', methods=['GET'])
def redeem_swipe(transaction_id):
    transaction = session.query(Transactions).filter_by(id=transaction_id).first()
    transaction.swipe_redeemed = True

    session.delete(transaction)
    session.commit()

    return redirect(url_for('index'))

@app.route('/<transaction_id>/cancel_transaction', methods=['GET'])
def cancel_transaction(transaction_id):
    transaction = session.query(Transactions).filter_by(id=transaction_id).first()

    session.delete(transaction)
    session.commit()

    return redirect(url_for('index'))

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
    def time_to_int(time):
        strRep = time.strftime("%H%M")
        return int(strRep)

    if request.method == "POST":
        timeRaw = request.form['timeSearch']
        time = datetime.datetime.strptime(timeRaw, '%H:%M')
        # time = int(time.strftime('%H%M'))

        sellers_raw = session.query(User).all()
        sellers = []

        for seller in sellers_raw:
            if seller.start_time != None and seller.end_time != None and seller.start_time.time() <= time.time() and seller.end_time.time() >= time.time():
                if seller.id != flask_login.current_user.id:
                    sellers.append(seller)

        sellers_data = []

        for seller in sellers:
            data = []

            data.append("Profile Picture")
            data.append(seller.name)
            data.append(seller.swipe_price)
            data.append(seller.id)

            sellers_data.append(data)

        return render_template("buy.html", sellers=sellers_data, time=timeRaw)
    else:
        current_time = datetime.datetime.now()
        time = current_time.strftime("%H:%M")

        return render_template("buy.html", sellers=[], time=time)


@app.route("/getOpenTransactions")
def getOpenTransactions():

    try:
        flask_login.current_user.id
    except:
        return jsonify(result=[])

#    transactions = session.query(Transactions).filter(and_(Transactions.seller == flask_login.current_user, Transactions.notified_status is False)).all()
    transactionsRaw = session.query(Transactions).all()
    transactions = []

    for transaction in transactionsRaw:
        if transaction.seller.id == flask_login.current_user.id and not transaction.notified_status:
            transactions.append(transaction)

    notifications = []

    for transaction in transactions:
        transaction.notified_status = True
        notifications.append(transaction.client.name + " would like to buy a swipe from you!")

    return jsonify(result=notifications)


def get_buyer_name(buyer_id):
    return session.query(User).filter(User.id == buyer_id).first().name


def notify(s):
    requests.post("https://maker.ifttt.com/trigger/daka_exchange/with/key/ct6p6W_232bEKEdkipWB90", data={'value1': s})


@app.route("/<buyer_id>/<seller_id>/createTransaction", methods=['GET', 'POST'])
def createTransaction(buyer_id, seller_id):
    seller = session.query(User).filter_by(id=seller_id).first()
    client = session.query(User).filter_by(id=buyer_id).first()

    new_transaction = Transactions(seller=seller, client=client)

    notify(seller.name + " would like to buy a swipe from you!")

    session.add(new_transaction)
    session.commit()

    return redirect(url_for('view_profile', user_id=buyer_id))
