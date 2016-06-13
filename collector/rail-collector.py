import argparse
import requests
import sqlite3
import xmltodict

# http://www.nationalrail.co.uk/100296.aspx
# https://lite.realtime.nationalrail.co.uk/OpenLDBWS/
# http://zetcode.com/db/sqlitepythontutorial/

# create table departures (crs TEXT, platform TEXT, std TEXT, etd TEXT, origin TEXT, destination TEXT);


xml_payload = """<?xml version="1.0"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns1="http://thalesgroup.com/RTTI/2014-02-20/ldb/" xmlns:ns2="http://thalesgroup.com/RTTI/2010-11-01/ldb/commontypes">
  <SOAP-ENV:Header>
    <ns2:AccessToken>
      <ns2:TokenValue>{KEY}</ns2:TokenValue>
    </ns2:AccessToken>
  </SOAP-ENV:Header>
  <SOAP-ENV:Body>
    <ns1:GetDepartureBoardRequest>
      <ns1:numRows>100</ns1:numRows>
      <ns1:crs>{CRS}</ns1:crs>
    </ns1:GetDepartureBoardRequest>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
"""


def fetch_trains(url, key, crs):
    headers = {'content-type': 'text/xml'}
    payload = xml_payload.replace("{KEY}", key).replace("{CRS}", crs)
    response = requests.post(url, data=payload, headers=headers)

    data = xmltodict.parse(response.content)
    services = data["soap:Envelope"]["soap:Body"]["GetDepartureBoardResponse"]["GetStationBoardResult"]["lt2:trainServices"]["lt2:service"]

    for service in services:
        yield {
            "crs": crs,
            "origin": service["lt2:origin"]["lt2:location"]["lt2:locationName"],
            "destination": service["lt2:destination"]["lt2:location"]["lt2:locationName"],
            "std": service.get("lt2:std"),
            "etd": service.get("lt2:etd"),
            "platform": service.get("lt2:platform", "?"),
        }


def insert_into_db(db, table, data):
    connection = sqlite3.connect(db)

    with connection:
        cursor = connection.cursor()
        for row in data:
            sql = "insert into {0} ({1}) values({2});".format(table, ",".join(row), ",".join(map(lambda key: '"{0}"'.format(row[key]), row)))
            print sql
            cursor.execute(sql)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='National Rail Data Collector')
    parser.add_argument('--key', help='API Key', required=True)
    parser.add_argument('--url', help='API URL', default="http://lite.realtime.nationalrail.co.uk/OpenLDBWS/ldb6.asmx")
    parser.add_argument('--crs', help='CRS Station Code (default is Thatcham)', default="THA")
    parser.add_argument('--db', help='SQLite DB Name', default="trains.db")
    args = parser.parse_args()

    departures = fetch_trains(args.url, args.key, args.crs)
    insert_into_db(args.db, "departures", departures)
