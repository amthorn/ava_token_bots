import requests
import re

from ciscosparkapi import CiscoSparkAPI

self_trigger_word = 'self'
pirate_url = 'http://pirate.monkeyness.com/cgi-bin/translator.pl'
pun_url = 'https://icanhazdadjoke.com/'

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
            '^.*[pP][iI][rR][aA][tT][eE].*$': self.pirate_translate,
            '^.*[pP][uU][nN].*$': self.pun,
            '^.*[cC][aA][tT]\s[fF][aA][cC][tT].*$': self.pun,
        }

    def handle(self, data):
        if self.api.people.me().id == data['personId']:
            # sent by me, check for first word is self
            message = self.api.messages.get(data['id']).text
            accept_message =  message.strip().startswith(self_trigger_word)
            if accept_message:
                message = message.replace(self_trigger_word, '', 1)
        else:
            message = self.api.messages.get(data['id']).text
            accept_message = True

        if accept_message and ((dms and data.get('roomType') == 'direct') or data['roomId'] in approved_rooms):
            message = message.replace(self.api.people.me().displayName, "", 1).strip()

            if data['personId'] == blake:
                self.api.messages.create(
                    markdown=pun(data, message),
                    roomId=data['roomId']
                )

            for regex, func in self.triggers.items():
                if re.search(regex, message):
                    self.api.messages.create(
                        markdown=preface + func(data, message),
                        roomId=data['roomId']
                    )
                    break

    def pirate_translate(self, data, message):
        return requests.get(
            pirate_url,
            params={
                'english': message,
                'version': 1.0
            }).text

    def pun(self, data, message):
        return requests.get(pun_url, headers={'Accept': 'application/json'}).json()['joke']
