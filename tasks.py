from model import User, get_users, get_celebrating

import flask
import requests
import app
import datetime


def send_message(user_id, message):
    app = flask.current_app
    token = app.config['BOT_TOKEN']

    url = 'https://api.telegram.org/bot%s/sendMessage' % token

    req = requests.get(url,
                       verify=False,
                       data={'chat_id': user_id, 'text': message})
    req.raise_for_status()


def message_admin(message):
    app = flask.current_app
    admin_id = int(app.config["ADMIN_ID"])

    send_message(admin_id, message)


@app.celery.task(name='pay')
def pay(user_id, amount, birthday_user_id, gift):
    user = User.query.get(user_id)
    birthday_user = User.query.get(birthday_user_id)

    name = []

    if birthday_user.first_name:
        name.append(birthday_user.first_name)

    if birthday_user.last_name:
        name.append(birthday_user.last_name)

    name = ' '.join(name)

    message = "We've withdrawn %s rub from your account for %s's birthday. Your balance is %s.\n\n" % (amount, name, int(user.balance))

    message = message + ("Gift: %s" % gift)

    send_message(user_id, message)


@app.celery.task(name='nudge_user')
def nudge_user(user_id, amount):
    app = flask.current_app
    cards = app.config['CARD_NUMBERS']

    message = "Your balance is low (%s rub). Please deposit an amount you are comfortable with at https://birthday.knazarov.com.\n\n" % amount

    cards_str = ', '.join(cards)

    message = message + "Alternatively you can do it through telegram. Transfer what you want to one of the cards: %s and type:\n/deposit <amount>" % cards_str

    send_message(user_id, message)


@app.celery.task(name='fill_balance')
def fill_balance(user_id, amount):
    user = User.query.get(user_id)

    message = "You've deposited %s rub. Your balance is %s rub" % (
        amount, int(user.balance))

    send_message(user_id, message)


@app.celery.task(name='need_approval')
def need_approval(user_id):
    app = flask.current_app
    admin_id = int(app.config["ADMIN_ID"])

    user = User.query.get(user_id)

    message = "User [%d] %s has just joined and needs approval. Type:\n/approve %d" % (
        user.id, user, user.id)

    send_message(admin_id, message)


@app.celery.task(name='nudge')
def nudge():
    for user in get_users():
        if user.balance < 200:
            print("Nudging user:", user)
            nudge_user.delay(int(user.id), user.balance)


@app.celery.task(name='send_news')
def send_news(user_id, text):
    send_message(user_id, text)


@app.celery.task(name='news')
def news(text):
    for user in get_users():
        send_news.delay(user.id, text)


@app.celery.task(name='notify_about_birthday')
def notify_about_birthday(user_id, birthday_user_id, days):
    user = User.query.get(birthday_user_id)

    if days == 14:
        left = "in 2 weeks"
    elif days == 7:
        left = "in a week"
    elif days == 1:
        left = "tomorrow"
    elif days == 0:
        left = "today"
    else:
        left = "in %d days" % days

    message = "%s has birthday %s" % (user.full_name(), left)

    send_message(user_id, message)


@app.celery.task(name='notify_about_own_birthday')
def notify_about_own_birthday(user_id, days):
    app = flask.current_app
    budget = int(app.config['BUDGET'])

    if days == 14:
        left = "in 2 weeks"
    elif days == 7:
        left = "in a week"
    elif days == 1:
        left = "tomorrow"
    elif days == 0:
        left = "today"
    else:
        left = "in %d days" % days

    message = "You have birthday %s. It is time to think about a present. Your budget is %d rub.\n\n" % (left, budget)

    message = message + "Please remember that you are responsible for picking a gift at least 7 days before celebration, so that the person responsible can buy it in time.\n\n"

    message = message + "If you don't want to celebrate your birthdays, type:\n/celebrate false"

    send_message(user_id, message)


@app.celery.task(name='notify_all_about_birthday')
def notify_all_about_birthday(birthday_user_id, days):
    for user in get_users():
        if user.id != birthday_user_id:
            notify_about_birthday.delay(user.id, birthday_user_id, days)


@app.celery.task(name='find_birthdays')
def find_birthdays():
    now = datetime.datetime.now().date()

    for user in get_celebrating():
        birthday = user.birthday

        if birthday is None:
            message_admin("User %s has no birthday set" % user)
            continue

        birthday = birthday.replace(year=now.year)

        days = (birthday-now).days

        if days < 0:
            continue

        print("User %s has %d days till birthday" % (user, days))

        if days == 20:
            notify_about_own_birthday.delay(user.id, days)

        if days in [14, 7, 1]:
            notify_all_about_birthday.delay(user.id, days)



@app.celery.task(name='find_incomplete_accounts')
def find_incomplete_accounts():
    for user in get_users():
        if user.birthday is None or user.phone is None:
            message_admin("User %s has incomplete accounts." % user.full_name())
