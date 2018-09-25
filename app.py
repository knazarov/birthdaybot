#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify, redirect
from flask_login import LoginManager, UserMixin
import hashlib
import hmac
import base64
import model
from database import init_database, db
from environment import read_config
import flask_security
import wtforms
import flask_assets
import datetime
from flask_security.utils import login_user
import flask_debugtoolbar
import flask
import flask_migrate
import forms

app = Flask(__name__)
read_config(app)

init_database(app)

security = flask_security.Security()
toolbar = flask_debugtoolbar.DebugToolbarExtension()
migrate = flask_migrate.Migrate()
assets = flask_assets.Environment()

assets.init_app(app)
toolbar.init_app(app)
migrate.init_app(app, db)

# User model
class ExtendedRegisterForm(flask_security.forms.ConfirmRegisterForm):
    name = wtforms.StringField('Name', [wtforms.validators.Required()])
    organization_name = wtforms.StringField(
        'Organization', [wtforms.validators.Required()])

# Setup Flask-Security
user_datastore = flask_security.SQLAlchemyUserDatastore(
    db, model.User, model.Role)
security._state = security.init_app(
    app, user_datastore,
    confirm_register_form=ExtendedRegisterForm)


@app.route('/', methods=['GET', 'POST'])
def index():
    if not flask_security.current_user.is_authenticated:
        return redirect('/login')

    user = flask_security.current_user
    print(user)

    cards = app.config['CARD_NUMBERS']

    form = forms.DepositForm()

    if form.validate_on_submit():
        amount = form.amount.data

        deposit = model.Deposit()
        deposit.amount = int(amount)
        print("amount: ", amount)
        user.deposits.append(deposit)
        db.session.add(deposit)
        db.session.commit()
        return flask.redirect(flask.url_for(
            'index'))

    return render_template('index.html', form=form, cards=cards)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

def string_generator(data_incoming):
    data = data_incoming.copy()
    del data['hash']
    keys = sorted(data.keys())
    string_arr = []
    print(keys)
    for key in keys:
        if data[key] is not None:
            print("key", key, data[key] or 'null')
            string_arr.append(key+'='+(data[key] or 'null'))
    string_cat = '\n'.join(string_arr)
    return string_cat


@app.route('/do_login')
def do_login():
    print(app.config['BOT_TOKEN'])

    if request.args.get('id', None) is None:
        return flask.abort(500)

    tg_data = {
        "id": request.args.get('id', None),
        "first_name": request.args.get('first_name', None),
        "last_name": request.args.get('last_name', None),
        "username": request.args.get('username', None),
        "photo_url": request.args.get('photo_url', None),
        "auth_date":  request.args.get('auth_date', None),
        "hash": request.args.get('hash', None)
    }
    data_check_string = string_generator(tg_data)
    secret_key = hashlib.sha256(
        app.config['BOT_TOKEN'].encode('utf-8')).digest()
    secret_key_bytes = secret_key
    data_check_string_bytes = bytes(data_check_string, 'utf-8')
    hmac_string = hmac.new(secret_key_bytes,
                           data_check_string_bytes,
                           hashlib.sha256).hexdigest()

    if hmac_string == tg_data['hash']:
        user = model.User.query.get(tg_data["id"])

        if user is None:
            user = model.User()
            user.id = tg_data["id"]
            user.first_name = tg_data["first_name"]
            user.last_name = tg_data["last_name"]
            user.username = tg_data["username"]
            user.active = True
            user.confirmed_at = datetime.datetime.now()
            db.session.add(user)
            db.session.commit()

        login_user(user)

        return redirect('/')

    return jsonify({
        'hmac_string': hmac_string,
        'tg_hash': tg_data['hash'],
        'tg_data': tg_data
    })

@app.route('/login')
def login():
    return render_template('login.html')


if __name__ == '__main__':
    context = ('server.crt', 'server.key')
    if app.config['DEBUG']:
        app.run(host="0.0.0.0", port=443, debug=True, ssl_context=context)
    else:
        app.run(host="0.0.0.0", port=5000)
