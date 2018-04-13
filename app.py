import flask
import traceback

from flask import Flask
from bot import Bot
from config import AVA_BOT, PRODUCTION
from ciscosparkapi import CiscoSparkAPI

app = Flask(__name__)
api = CiscoSparkAPI(AVA_BOT)

@app.route('/', methods=['POST'])
def index():
    try:
        if hasattr(flask.request, 'json') and flask.request.json.get('data'):
            bot = Bot(api)
            bot.handle(flask.request.json['data'])

    except Exception as e:
        # text back error
        print(traceback.format_exc())
        if not PRODUCTION:
            raise e
    return ''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9988, debug=True)