import json
import urllib
import urllib2

import feedparser
from flask import Flask, render_template, request

app = Flask(__name__)

RSS_FEEDS = {
    'ign': 'http://feeds.ign.com/ign/all',
    'gamespot': 'https://www.gamespot.com/feeds/mashup/',
    'gameinformer': 'http://www.gameinformer.com/feeds/thefeedrss.aspx'
}

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=3a25fdec16ef01628221824762a81879"
CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=26de8120d6a84912a43877e992cc316e"

DEFAULTS = {
    'publication': 'ign',
    'city': 'London, UK',
    'currency_from': 'GDP',
    'currency_to': 'USD'
}


@app.route("/")
def home():
    publication = request.args.get("publication")
    if not publication or publication.lower() not in RSS_FEEDS:
        publication = DEFAULTS['publication']
    articles = get_news(publication.lower())

    city = request.args.get("city")
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)

    return render_template("home.html", articles=articles, weather=weather)


def get_news(publication):
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']


def get_weather(query):
    query = urllib.quote(query)
    url = WEATHER_URL.format(query)
    data = urllib2.urlopen(url).read()
    parsed = json.loads(data)
    weather = None

    if parsed.get('weather'):
        weather = {
            'description': parsed['weather'][0]['description'],
            'temperature': parsed['main']['temp'],
            'city': parsed['name'],
            'country': parsed['sys']['country']
        }
    return weather


if __name__ == '__main__':
    app.run(port=5000, debug=True)
