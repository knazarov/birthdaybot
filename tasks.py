from model import User
import flask
import requests
import app

def send_message(user_id, message):
    app = flask.current_app
    token = app.config['BOT_TOKEN']

    url = 'https://api.telegram.org/bot%s/sendMessage' % token

    req = requests.get(url,
                       verify=False,
                       data={'chat_id': user_id, 'text': message})
    req.raise_for_status()


@app.celery.task(name='pay')
def pay(user_id, amount, birthday_user_id):
    user = User.query.get(user_id)
    birthday_user = User.query.get(birthday_user_id)

    name = []

    if birthday_user.first_name:
        name.append(birthday_user.first_name)

    if birthday_user.last_name:
        name.append(birthday_user.last_name)

    name = ' '.join(name)

    message = "We've withdrawn %s rub from your account for %s's birthday. Your balance is %s" % (amount, name, user.balance)

    send_message(user_id, message)


@app.celery.task(name='nudge_user')
def nudge_user(user_id, amount):
    message = "Your balance low (%s rub). Please deposit an amount you are comfortable with at https://birthday.knazarov.com." % amount

    send_message(user_id, message)




@app.celery.task(name='fill_balance')
def fill_balance(user_id, amount):
    user = User.query.get(user_id)

    message = "You've deposited %s rub. Your balance is %s rub" % (
        amount, user.balance())

    send_message(user_id, message)


@app.celery.task(name='nudge')
def nudge():
    for user in User.query.all():
        if user.balance() < 200:
            nudge_user.delay(int(user.id), user.balance())
