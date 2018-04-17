import feedparser
from flask import Flask, render_template

app = Flask(__name__)

RSS_FEEDS = {
    'ign': 'http://feeds.ign.com/ign/all',
    'gamespot': 'https://www.gamespot.com/feeds/mashup/',
    'gameinformer': 'http://www.gameinformer.com/feeds/thefeedrss.aspx'

}


@app.route("/")
@app.route("/<publication>")
def get_news(publication="ign"):
    feed = feedparser.parse(RSS_FEEDS[publication])
    articles = feed['entries']
    return render_template("home.html", articles=articles)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
