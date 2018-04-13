import requests
import random
import json
from bs4 import BeautifulSoup

response = requests.get('https://en.wikiquote.org/w/api.php?action=parse&page=SpongeBob_SquarePants&format=json')
season_links = [i['*'] for i in response.json()['parse']['links'] if 'Season' in i['*']]

quotes = []

for season_link in season_links:
    season_response = requests.get(
        'https://en.wikiquote.org/w/api.php?action=parse&page=' + season_link + '&format=json'
    )
    text = season_response.json()['parse']['text']['*']
    soup = BeautifulSoup(text, 'html.parser')
    quotes += [i.text for i in soup.find_all('dl')]

json.dump(quotes, open('spongebob.json', 'w'))
