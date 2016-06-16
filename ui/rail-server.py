import argparse
import sqlite3
from flask import Flask, jsonify, send_from_directory

# http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
from werkzeug.utils import redirect

app = Flask(__name__)


def read_calling_points(all_points):
    points = []

    for point_str in all_points.split("|"):
        splits = point_str.strip().split(",")

        if len(splits) != 4:
            continue

        points.append({
            "crs": splits[0],
            "name": splits[1],
            "st": splits[2],
            "et": splits[3]
        })

    return points


def fetch_departures(crs=None):
    connection = sqlite3.connect(db)

    with connection:
        cursor = connection.cursor()
        sql = "select crs, origin, destination, std, etd, platform, calling_points from {0};".format("departures")
        if crs is not None:
            sql = sql.replace(";", " where crs = '{0}';".format(crs))
        sql = sql.replace(";", " order by std asc;")
        cursor.execute(sql)
        rows = cursor.fetchall()

    return map(lambda row: {
        "crs": row[0],
        "origin": row[1],
        "destination": row[2],
        "std": row[3],
        "etd": row[4],
        "platform": row[5],
        "calling_points": read_calling_points(row[6])
    }, rows)


def crs_to_name(crs):
    connection = sqlite3.connect(db)

    with connection:
        cursor = connection.cursor()
        cursor.execute("select name from stations where crs = '{0}'".format(crs))
        rows = cursor.fetchall()
        return rows[0][0]


def get_location(crs):
    connection = sqlite3.connect(db)

    with connection:
        cursor = connection.cursor()
        cursor.execute("select latitude, longitude from stations where crs = '{0}'".format(crs))
        rows = cursor.fetchall()
        if len(rows) >= 1:
            return rows[0][0], rows[0][1]
        else:
            return None, None


def add_location(station):
    lat, lon = get_location(station["crs"])
    station["latitude"] = lat
    station["longitude"] = lon
    return station


def service_to_route(service):
    crs_point = {
        "crs": service["crs"],
        "name": crs_to_name(service["crs"]),
        "st": service.get("std", "-"),
        "et": service.get("etd", "-")
    }

    route = service["calling_points"]
    route.insert(0, crs_point)
    route = map(add_location, route)
    return route


def fetch_routes_for(crs=None):
    departures = fetch_departures(crs)
    routes = map(service_to_route, departures)
    return routes


def fetch_stations(crs=None):
    connection = sqlite3.connect(db)

    with connection:
        cursor = connection.cursor()
        sql = "select crs, name, latitude, longitude from {0};".format("stations")
        if crs is not None:
            sql = sql.replace(";", " where crs = '{0}';".format(crs))
        sql = sql.replace(";", " order by name asc;")
        cursor.execute(sql)
        rows = cursor.fetchall()

    return map(lambda row: {
        "crs": row[0],
        "name": row[1],
        "latitude": row[2],
        "longitude": row[3]
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
                        <h2>UI</h2>
                        <p>Departure board <a href="/departure-board">/departure-board</a></p>
                        <h2>REST API</h2>
                        <p>To get a list of all departures in the DB, hit <a href="/departures">/departures</a></p>
                        <p>
                            Or you can hit /depratures/[CRS] with a station code (CRS) like
                            <a href="/departures/PAD">/departures/PAD</a>
                            or <a href="/departures/THA">/departures/THA</a>.
                        </p>
                    </body>
                </html>
            """


@app.route('/route-map')
def route_map_index_html():
    return redirect("/route-map/index.html", code=302)


@app.route('/route-map/<path:path>')
def route_map_static_files(path):
    return send_from_directory('route-map', path)


@app.route('/departure-board/')
def departure_board_index_html():
    return redirect("/departure-board/index.html", code=302)


@app.route('/departure-board/<path:path>')
def departure_board_static_files(path):
    return send_from_directory('departure-board', path)


@app.route('/stations')
def stations():
    return jsonify(fetch_stations())


@app.route('/departures')
def departures():
    return jsonify(fetch_departures())


@app.route('/departures/<string:crs>')
def departures_for(crs):
    return jsonify(fetch_departures(crs))


@app.route('/routes/<string:crs>')
def routes_for(crs):
    return jsonify(fetch_routes_for(crs))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='National Rail Data REST Server')
    parser.add_argument('--db', help='SQLite DB Name', default="../data/trains.db")
    args = parser.parse_args()

    db = args.db

    app.run(debug=True)
