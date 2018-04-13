import flask

from flask import Flask
from bot import Bot

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    try:
        if hasattr(flask.request, 'json') and flask.request.json.get('data'):
            bot = Bot()
            bot.handle(flask.request.json['data'])

    except Exception as e:
        # text back error
        raise e
    return ''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9988, debug=True)