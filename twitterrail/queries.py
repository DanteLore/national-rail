import requests
import xmltodict


class MockQueries:
    def __init__(self, services=None):
        self.services = services

    def services_between(self, origin, destination):
        return self.services


class RealQueries:
    def __init__(self, url, key):
        self.url = url
        self.headers = {'content-type': 'text/xml'}
        self.xml_payload = """<?xml version="1.0"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns1="http://thalesgroup.com/RTTI/2016-02-16/ldb/" xmlns:ns2="http://thalesgroup.com/RTTI/2013-11-28/Token/types">
  <SOAP-ENV:Header>
    <ns2:AccessToken>
      <ns2:TokenValue>{KEY}</ns2:TokenValue>
    </ns2:AccessToken>
  </SOAP-ENV:Header>
  <SOAP-ENV:Body>
    <ns1:GetDepBoardWithDetailsRequest>
      <ns1:numRows>20</ns1:numRows>
      <ns1:crs>{ORIG}</ns1:crs>
      <ns1:filterCrs>{DEST}</ns1:filterCrs>
      <ns1:filterType>to</ns1:filterType>
      <ns1:timeWindow>120</ns1:timeWindow>
    </ns1:GetDepBoardWithDetailsRequest>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
""".replace("{KEY}", key)

    def services_between(self, origin, destination):
        xml = self.xml_payload\
            .replace("{ORIG}", origin)\
            .replace("{DEST}", destination)
        response = requests.post(self.url, data=xml, headers=self.headers)

        data = xmltodict.parse(response.content)
        response = data["soap:Envelope"]["soap:Body"]["GetDepBoardWithDetailsResponse"]["GetStationBoardResult"]

        if "lt5:trainServices" in response:
            services = response["lt5:trainServices"]["lt5:service"]

            if type(services) is not list:
                services = [services]

            for service in services:
                yield {
                    "crs": origin,
                    "origin": service["lt5:origin"]["lt4:location"]["lt4:locationName"],
                    "destination": service["lt5:destination"]["lt4:location"]["lt4:locationName"],
                    "std": service.get("lt4:std"),
                    "etd": service.get("lt4:etd"),
                    "platform": service.get("lt4:platform", "-")
                }
