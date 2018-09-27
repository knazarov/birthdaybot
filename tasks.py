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
