#!/usr/bin/env python3

import requests
import flask
import time
import model
import traceback
import tasks
import datetime

from app import app, celery, db

update_id = 0


def send_message(user_id, message):
    app = flask.current_app
    token = app.config['BOT_TOKEN']

    url = 'https://api.telegram.org/bot%s/sendMessage' % token

    req = requests.get(url,
                       verify=False,
                       data={'chat_id': user_id, 'text': message})
    req.raise_for_status()


def deposit(user, params):
    if len(params) == 0:
        send_message(user.id, "Please specify amount to deposit")
        return

    amount_str = params[0]

    if not amount_str.isdigit():
        send_message(user.id, "Amount must be a positive integer")
        return

    amount = int(amount_str)

    deposit = model.Deposit()
    deposit.amount = amount
    deposit.timestamp = datetime.datetime.utcnow()

    user.deposits.append(deposit)
    db.session.add(deposit)
    db.session.commit()

    tasks.fill_balance.delay(user.id, amount)


def approve(user, params):
    if not model.is_admin(user.id):
        send_message(user.id, "Only admins can do that")
        return

    if len(params) == 0:
        send_message(user.id, "Please specify user id")
        return

    userid_str = params[0]

    if not userid_str.isdigit():
        send_message(user.id, "User id must be a positive integer")
        return

    user_id = int(userid_str)

    to_approve = model.User.query.get(user_id)

    if to_approve is None:
        send_message(user.id, "No such user")
        return

    to_approve.approved = True
    db.session.commit()

    send_message(user.id, "Approved user: %s" % to_approve)


def participate_text(user):
    if not user.participates:
        return "You are not participating in any way"
    elif not user.celebrates:
        return "You are participating in other people birthdays but not celebrating yours"
    else:
        return "You are participating in other people birthdays and celebrating yours"

    return ""

def participate(user, params):
    if len(params) == 0:
        send_message(user.id, "Please specify 'true' or 'false'")
        return

    is_participate = params[0].lower()


    if is_participate not in ["true", "false"]:
        send_message(user.id, "Please specify 'true' or 'false'")
        return

    user.participates = is_participate == "true"
    db.session.commit()

    send_message(user.id, participate_text(user))


def celebrate(user, params):
    if len(params) == 0:
        send_message(user.id, "Please specify 'true' or 'false'")
        return

    is_celebrate = params[0].lower()

    if is_celebrate not in ["true", "false"]:
        send_message(user.id, "Please specify 'true' or 'false'")
        return

    user.celebrates = is_celebrate == "true"
    db.session.commit()

    send_message(user.id, participate_text(user))


def chat(user, params):
    if len(params) == 0:
        send_message(user.id, "Please specify 'true' or 'false'")
        return

    is_chat = params[0].lower()

    if is_chat not in ["true", "false"]:
        send_message(user.id, "Please specify 'true' or 'false'")
        return

    user.chats = is_chat == "true"
    db.session.commit()

    if is_chat == "true":
        send_message(user.id, "You will be added to birthday chats")
    else:
        send_message(user.id, "You won't be added to birthday chats")


def handle_command(user_id, command, params):
    if not model.is_authorized(user_id):
        send_message(user_id, "You are not authorized to send commands. Please ask server admin to authorize you.")
        return

    user = model.User.query.get(user_id)

    print("command", user, command, params)

    if command == "deposit":
        deposit(user, params)
    elif command == "approve":
        approve(user, params)
    elif command == "participate":
        participate(user, params)
    elif command == "celebrate":
        celebrate(user, params)
    elif command == "chat":
        chat(user, params)


def handle_update(update):
    if "message" not in update:
        return

    message = update["message"]

    if message["from"]["is_bot"]:
        return

    user_id = message["from"]["id"]

    text = message["text"]

    print(user_id, text)

    if text.startswith('/'):
        parts = text.split(' ')
        command = parts[0].lstrip('/')
        handle_command(user_id, command, parts[1:])


def get_updates():
    app = flask.current_app
    global update_id

    token = app.config['BOT_TOKEN']

    url = 'https://api.telegram.org/bot%s/getUpdates' % token

    data = {"timeout": 10}

    #print("update id", update_id)

    if update_id != 0:
        data["offset"] = update_id + 1

    req = requests.get(url, data=data)
    req.raise_for_status()

    data=req.json()

    if not data["ok"]:
        return

    result = data["result"]

    for entry in result:
        update_id = max(update_id, entry["update_id"])
        handle_update(entry)


def main():
    app.app_context().push()

    while True:
        try:
            get_updates()
        except Exception as ex:
            traceback.print_exc()
            time.sleep(1)


if __name__ == "__main__":
    main()
