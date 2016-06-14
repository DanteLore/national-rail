import argparse
from time import sleep

import requests
import xmltodict

# http://www.nationalrail.co.uk/100296.aspx
# https://lite.realtime.nationalrail.co.uk/OpenLDBWS/
# http://zetcode.com/db/sqlitepythontutorial/

# create table departures (crs TEXT, platform TEXT, std TEXT, etd TEXT, origin TEXT, destination TEXT, calling_points TEXT);
from utils.database import insert_into_db, delete_where

xml_payload = """<?xml version="1.0"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns1="http://thalesgroup.com/RTTI/2016-02-16/ldb/" xmlns:ns2="http://thalesgroup.com/RTTI/2013-11-28/Token/types">
  <SOAP-ENV:Header>
    <ns2:AccessToken>
      <ns2:TokenValue>{KEY}</ns2:TokenValue>
    </ns2:AccessToken>
  </SOAP-ENV:Header>
  <SOAP-ENV:Body>
    <ns1:GetDepBoardWithDetailsRequest>
      <ns1:numRows>12</ns1:numRows>
      <ns1:crs>{CRS}</ns1:crs>
      <ns1:timeWindow>120</ns1:timeWindow>
    </ns1:GetDepBoardWithDetailsRequest>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
"""


def fetch_trains(url, key, crs):
    headers = {'content-type': 'text/xml'}
    payload = xml_payload.replace("{KEY}", key).replace("{CRS}", crs)
    response = requests.post(url, data=payload, headers=headers)

    data = xmltodict.parse(response.content)
    services = data["soap:Envelope"]["soap:Body"]["GetDepBoardWithDetailsResponse"]["GetStationBoardResult"]["lt5:trainServices"]["lt5:service"]

    for service in services:
        raw_points = service["lt5:subsequentCallingPoints"]["lt4:callingPointList"]["lt4:callingPoint"]

        calling_points = map(lambda point: {
            "crs": point["lt4:crs"],
            "name": point["lt4:locationName"],
            "st": point.get("lt4:st", "-"),
            "et": point.get("lt4:et", "-")
        }, raw_points)

        cp_string = "|".join(
                map(lambda p: "{0},{1},{2},{3}".format(p["crs"], p["name"], p["st"], p["et"]), calling_points)
        )

        yield {
            "crs": crs,
            "origin": service["lt5:origin"]["lt4:location"]["lt4:locationName"],
            "destination": service["lt5:destination"]["lt4:location"]["lt4:locationName"],
            "std": service.get("lt4:std"),
            "etd": service.get("lt4:etd"),
            "platform": service.get("lt4:platform", "-"),
            "calling_points": cp_string
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='National Rail Data Collector')
    parser.add_argument('--key', help='API Key', required=True)
    parser.add_argument('--url', help='API URL', default="http://lite.realtime.nationalrail.co.uk/OpenLDBWS/ldb9.asmx")
    parser.add_argument('--crs', help='CRS Station Code (default is Thatcham)', default="THA")
    parser.add_argument('--db', help='SQLite DB Name', default="../data/trains.db")
    args = parser.parse_args()

    while True:
        departures = fetch_trains(args.url, args.key, args.crs)
        delete_where(args.db, "departures", "crs == '{0}'".format(args.crs))
        insert_into_db(args.db, "departures", departures)
        sleep(10)
