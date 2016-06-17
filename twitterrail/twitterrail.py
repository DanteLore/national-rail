import argparse
from tweeting import RealTweeterApi
from queries import RealQueries


class RailTweeter:
    def __init__(self, tweeter, queries):
        self.tweeter = tweeter
        self.queries = queries

    def do_it(self):
        services = self.queries.services_between("PAD", "THA")

        print list(services)
        message = "\n".join(
            map(lambda ser: "{0} {1} {2}".format(ser["std"], ser["destination"], ser["etd"]), services)
        )
        message = "Paddington to Thatcham:\n" + message

        self.tweeter.tweet(message)
        #self.tweeter.message("DanteLore", "Yo yo")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tweeting about railways')
    parser.add_argument('--rail-key', help='API Key', required=True)
    parser.add_argument('--consumer-key', help='Consumer Key', required=True)
    parser.add_argument('--consumer-secret', help='Consumer Secret', required=True)
    parser.add_argument('--access-token', help='Access Token', required=True)
    parser.add_argument('--access-token-secret', help='Access Token Secret', required=True)
    parser.add_argument('--url', help='API URL', default="http://lite.realtime.nationalrail.co.uk/OpenLDBWS/ldb9.asmx")
    args = parser.parse_args()

    twitter = RealTweeterApi(args.consumer_key, args.consumer_secret, args.access_token, args.access_token_secret)
    queries = RealQueries(args.url, args.rail_key)
    rt = RailTweeter(twitter, queries)
    rt.do_it()
