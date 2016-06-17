import argparse

from osgb import osgb_to_lonlat
from osgb.convert import eastnorth_to_osgb
from utils.database import insert_into_db, empty_table


# Loads data from here: https://data.gov.uk/dataset/naptan

# create table stations (crs TEXT, name TEXT, easting INT, northing INT, latitude DOUBLE, longitude DOUBLE);


def read_stations(filename):
    with open(filename, 'r') as input_file:
        for line in input_file.readlines()[1:]:
            splits = line.strip().split(",")
            yield {
                "crs": splits[2],
                "name": splits[3],
                "easting": long(splits[6]),
                "northing": long(splits[7])
            }


def convert(row):
    e = row["easting"]
    n = row["northing"]
    lon, lat = osgb_to_lonlat(eastnorth_to_osgb(e, n, digits=4))

    row["latitude"] = lat
    row["longitude"] = lon

    return row


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='National Rail Data Collector')
    parser.add_argument('--filename', help='Input CSV file', default="../data/RailReferences.csv")
    parser.add_argument('--db', help='SQLite DB Name', default="../data/trains.db")
    args = parser.parse_args()

    rows = read_stations(args.filename)
    stations = map(convert, rows)
    empty_table(args.db, "stations")
    insert_into_db(args.db, "stations", stations)
