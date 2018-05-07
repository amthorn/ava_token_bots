import requests
import re
import urllib
import os
import json
import random

from ciscosparkapi import CiscoSparkAPI
from config import PRODUCTION

self_trigger_word = 'self' if PRODUCTION else 'dev'
pirate_url = 'http://pirate.monkeyness.com/cgi-bin/translator.pl'
pun_url = 'https://icanhazdadjoke.com/'
cat_fact_url = 'https://catfact.ninja/fact'
dog_pic_url = 'https://api.thedogapi.co.uk/v2/dog.php'
cat_pic_url = 'http://thecatapi.com/api/images/get?format=src&type=gif'
magic_eight_ball_url = 'https://yesno.wtf/api/'
ron_swanson_url = 'https://ron-swanson-quotes.herokuapp.com/v2/quotes'

approved_rooms = [
    'Y2lzY29zcGFyazovL3VzL1JPT00vYjA3NGRhMTAtZGViZS0xMWU3LWI5OGYtYTcwZDc1YjVjZGYw',   # QA MEME
    'Y2lzY29zcGFyazovL3VzL1JPT00vNTA1MDY3YjAtMzM3Zi0xMWU4LThhYmEtMjE3NDEyMGI1ZjU0',  # TEST2
    'Y2lzY29zcGFyazovL3VzL1JPT00vODQxYmJkMTAtZTI0NS0xMWU2LWE5YmUtNGQxN2YxMzBjNzJk',  # GENERAL
]

blake = 'Y2lzY29zcGFyazovL3VzL1BFT1BMRS81MWYxMmUwOC0wYjRiLTQ3MzMtYmJjOC0zY2NiZjE3NWE0YTk'

preface = ''
dms = True

class Bot:
    def __init__(self, api):
        self.api = api
        self.triggers = {
            '^.*[pP][uU][nN].*$': self.pun,
            '^.*[pP][iI][rR][aA][tT][eE].*$': self.pirate_translate,
            '^.*[cC][aA][tT]\s[fF][aA][cC][tT].*$': self.cat_fact,
            '^.*[dD][oO][gG]\s[pP][iI][cC].*$': self.dog_pic,
            '^.*[cC][aA][tT]\s[pP][iI][cC].*$': self.cat_pic,
            '^.*[sS][pP][oO][nN][gG][eE][bB][oO][bB].*$': self.spongebob,
            '^.*#[sS][hH][rR][uU][gG][sS].*$': self.shrugs,
            '^.*#[rR][iI][pP].*$': self.rip,
            # '^.*[rR][oO][nN]\s[sS][wW][aA][nN][sS][oO][nN].*$': self.ron,
            '^.*[mM][aA][gG][iI][cC]\s[eE][iI][gG][hH][tT](\s)?[bB][aA][lL][lL].*$': self.magic_eight_ball,
            '^.*[vV][oO][tT][eE][bB][oO][tT].*$': self.vote_bot,
        }
        self.trigger_word_appears = False

    def handle(self, data):
        if self.api.people.me().id == data['personId']:
            # sent by me, check for first word is self
            message = self.api.messages.get(data['id']).text
            if message:
                accept_message =  message.strip().startswith(self_trigger_word)
                if accept_message:
                    message = message.replace(self_trigger_word, '', 1)
                    self.trigger_word_appears = True
            else:
                accept_message = False
        else:
            message = self.api.messages.get(data['id']).text
            accept_message = True

        if not PRODUCTION and self.trigger_word_appears or PRODUCTION:
            if accept_message and ((dms and data.get('roomType') == 'direct') or data['roomId'] in approved_rooms):
                message = message.replace(self.api.people.me().displayName, "", 1).strip()

                # if data['personId'] == blake:
                #     pun(data, message)

                for regex, func in self.triggers.items():
                    if re.search(regex, message):
                        func(data, message)
                        break

    def pirate_translate(self, data, message):
        message =  requests.get(
            pirate_url,
            params={
                'english': message,
                'version': 1.0
            }).text

        self.api.messages.create(
            markdown=preface + message,
            roomId=data['roomId']
        )

    def pun(self, data, message):
        message = requests.get(pun_url, headers={'Accept': 'application/json'}).json()['joke']

        self.api.messages.create(
            markdown=preface + message,
            roomId=data['roomId']
        )

    def cat_fact(self, data, message):
        message = requests.get(cat_fact_url).json()['fact']

        self.api.messages.create(
            markdown=preface + message,
            roomId=data['roomId']
        )

    def ron(self, data, message):
        message = requests.get(ron_swanson_url).json()[0]

        self.api.messages.create(
            markdown=preface + message,
            roomId=data['roomId']
        )

    def dog_pic(self, data, message):
        response = requests.get(dog_pic_url)
        if response.status_code == 200:
            url = response.json()['data'][0]['url']
            filename = 'dog_pic.' + response.json()['data'][0]['format']
            with open(filename, 'wb') as file:
                file.write(requests.get(url).content)

            self.api.messages.create(
                markdown=preface,
                files=[filename],
                roomId=data['roomId']
            )
            try:
                os.remove(filename)
            except OSError:
                pass

    def cat_pic(self, data, message):
        response = requests.get(cat_pic_url)
        if response.status_code == 200:
            filename = 'cat_pic.gif'
            with open(filename, 'wb') as file:
                file.write(response.content)

            self.api.messages.create(
                markdown=preface,
                files=[filename],
                roomId=data['roomId']
            )
            try:
                os.remove(filename)
            except OSError:
                pass

    def magic_eight_ball(self, data, message):
        response = requests.get(magic_eight_ball_url)
        if response.status_code == 200:
            filename = 'magic_eight_ball.gif'
            with open(filename, 'wb') as file:
                file.write(requests.get(response.json()['image']).content)

            self.api.messages.create(
                markdown=preface + response.json()['answer'],
                files=[filename],
                roomId=data['roomId']
            )
            try:
                os.remove(filename)
            except OSError:
                pass

    def spongebob(self, data, message):
        try:
            self.api.messages.create(
                markdown=preface + random.choice(json.load(open('spongebob.json'))).replace('\n', '\n\n'),
                roomId=data['roomId']
            )
        except FileNotFoundError:
            pass

        # Update quotes
        import spongebob_quote_getter


    def shrugs(self, data, message):
        self.api.messages.create(
            markdown=preface + r'¯\\\_(ツ)\_/¯',
            roomId=data['roomId']
        )

    def rip(self, data, message):
        self.api.messages.create(
            files=['rip.png'],
            roomId=data['roomId']
        )

    def vote_bot(self, data, message):
        me = self.api.people.me()

        message_id = request['data']['id']
        message = self.api.messages.get(message_id).text

        if message.startswith("new vote"):
            options = [i.strip() for i in message.replace("new vote", "", 1).strip().split(' ')]
            votes = {}
            for i in options:
                votes[i] = []

            json.dump(votes, open('votes.json', 'w'))
            self.api.messages.create(
                roomId=request['data']['roomId'],
                markdown="Let the voting begin. Tag me with your case-sensitive vote!"
            )
        elif message == 'talley':
            votes = json.load(open('votes.json', 'r'))
            self.api.messages.create(roomId=request['data']['roomId'], markdown=self.as_markdown(votes))
        else:
            votes = json.load(open('votes.json', 'r'))
            if message in votes:
                votes[message].append(self.api.people.get(request['data']['personId']).displayName)
                votes[message] = list(set(votes[message]))
                json.dump(votes, open('votes.json', 'w'))
                self.api.messages.create(roomId=request['data']['roomId'], markdown=self.as_markdown(votes))
            else:
                self.api.messages.create(
                    roomId=request['data']['roomId'],
                    markdown="'" + str(message) + "' not a valid option, please use one of: " + ', '.join(list(votes.keys()))
                )

        return 'OK'

    def as_markdown(self, votes):
        message = ''
        for k, v in votes.items():
            message += str(k) + ': ' + str(len(v)) + ((' (' + ', '.join(v) + ')\n\n') if len(v) else '\n\n')
        return message


