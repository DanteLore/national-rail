import argparse
import sqlite3
from flask import Flask, jsonify

# http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

app = Flask(__name__)


def fetch_departures(table, crs=None):
    connection = sqlite3.connect(db)

    with connection:
        cursor = connection.cursor()
        sql = "select crs, origin, destination, std, etd, platform from {0};".format(table)
        if crs is not None:
            sql = sql.replace(";", " where crs = '{0}';").format(crs)
        cursor.execute(sql)
        rows = cursor.fetchall()

    return map(lambda row: {
        "crs": row[0],
        "origin": row[1],
        "destination": row[2],
        "std": row[3],
        "etd": row[4],
        "platform": row[5]
    }, rows)


@app.route('/')
def index():
    return """
                <html>
                    <head>
                        <title>Real Time Train REST API</title>
                    </head>
                    <body>
                        <h1>Real Time Train REST API</h1>
                        <p>To get a list of all departures in the DB, hit <a href="/departures">/departures</a></p>
                        <p>
                            Or you can hit /depratures/[CRS] with a station code (CRS) like
                            <a href="/departures/PAD">/departures/PAD</a>
                            or <a href="/departures/THA">/departures/THA</a>.
                        </p>
                    </body>
                </html>
            """


@app.route('/departures')
def departures():
    return jsonify(fetch_departures("departures"))


@app.route('/departures/<string:crs>')
def departures_for(crs):
    return jsonify(fetch_departures("departures", crs))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='National Rail Data REST Server')
    parser.add_argument('--db', help='SQLite DB Name', default="../data/trains.db")
    args = parser.parse_args()

    db = args.db

    app.run(debug=True)
