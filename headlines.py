import datetime
import json
import urllib
import urllib2

import feedparser
from flask import Flask, render_template, request, make_response

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
    'currency_from': 'GBP',
    'currency_to': 'USD'
}


@app.route("/")
def home():
    publication = get_value_with_fallback("publication")
    articles = get_news(publication.lower())

    city = get_value_with_fallback("city")
    weather = get_weather(city)

    currency_from = get_value_with_fallback("currency_from")
    currency_to = get_value_with_fallback("currency_to")
    rate, currencies = get_rate(currency_from, currency_to)

    response = make_response(
        render_template(
            "home.html",
            articles=articles,
            weather=weather,
            currency_from=currency_from,
            currency_to=currency_to,
            rate=rate,
            currencies=sorted(currencies)
        )
    )
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)

    return response


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


def get_rate(frm, to):
    all_currency = urllib2.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return to_rate / frm_rate, parsed.keys()


def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]


if __name__ == '__main__':
    app.run(port=5000, debug=True)
