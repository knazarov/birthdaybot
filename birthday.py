#!/usr/bin/env python3

import sys
import json
import datetime
import dateparser

from telethon import TelegramClient, sync
from telethon.tl.functions.messages import CreateChatRequest

api_id = 123456
api_hash = 'ilikerandompasswords'

client = TelegramClient('birthdaybot', api_id, api_hash)

team = None
with open('team.json') as f:
    team = json.loads(f.read())

def find_birthday_chat(client, person):
    dialogs = client.get_dialogs()
    now = datetime.datetime.now()
    for dialog in dialogs:
        if (now - dialog.date).days < 30 and \
           person in dialog.name and \
           'birthday' in dialog.name:
            return dialog

def create_birthday_chat(client, team, current_birthday):
    names = set([n for n in team.keys()])

    if current_birthday not in names:
        sys.exit('Unknown person: %s' % current_birthday)

    all_except_birthday_person = names - set([current_birthday])
    invitee_phones = [team[n][0] for n in all_except_birthday_person]
    birthday = team[current_birthday][1]

    client(CreateChatRequest(invitee_phones, '%s birthday: %s' %
                             (current_birthday, birthday)))


def find_birthdays(client, team):
    for person in team.keys():
        birthday = dateparser.parse(team[person][1])
        now = datetime.datetime.now()

        if abs((now - birthday).days) < 14:
            print("%s has birthday on %s" % (person, birthday))

            dialog = find_birthday_chat(client, person)

            if dialog is not None:
                print("Birthday chat already created")
            else:
                print("Creating birthday chat")
                create_birthday_chat(client, team, person)

client.start()
find_birthdays(client, team)
