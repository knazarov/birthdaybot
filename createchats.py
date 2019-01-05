#!/usr/bin/env python3

import sys
import json
import datetime
import dateparser
import requests
import os
import configparser

from telethon import TelegramClient, sync
from telethon.tl.functions.messages import CreateChatRequest


def find_birthday_chat(client, person):
    dialogs = client.get_dialogs()
    now = datetime.datetime.now(datetime.timezone.utc)
    for dialog in dialogs:
        if (now - dialog.date).days < 30 and \
           person in dialog.name and \
           'birthday' in dialog.name:
            return dialog


def find_birthdays(client, token):
    url = "https://birthday.knazarov.com/birthdays?token=%s" % token

    req = requests.get(url)
    req.raise_for_status()

    res = req.json()

    for birthday in res:
        person = birthday["name"]
        date = birthday["date"]
        invitees = birthday["invitees"]

        dialog = find_birthday_chat(client, person)

        if dialog is not None:
            print("Birthday chat already exists for %s" % person)
        else:
            print("Creating birthday chat for %s" % person)
            client(CreateChatRequest(invitees, '%s birthday: %s' %
                                     (person, date)))


def main():
    config = configparser.ConfigParser()

    config.read(os.path.expanduser("~/.birthday.ini"))

    api_id = int(config['default']['api_id'])
    api_hash = config['default']['api_hash']
    token = config['default']['token']

    client = TelegramClient('birthdaybot', api_id, api_hash)

    client.start()
    find_birthdays(client, token)


if __name__ == "__main__":
    main()
