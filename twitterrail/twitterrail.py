import argparse
from tweeting import RealTweeterApi
from queries import RealQueries

emoji_skull = "\xF0\x9F\x92\x80"
emoji_tick = "\xE2\x9C\x94"
emoji_cross = "\xE2\x9C\x96"
emoji_train = "\xF0\x9F\x9A\x84"
emoji_late = "\xF0\x9F\x95\x93"


class RailTweeter:
    def __init__(self, tweeter, queries, origin, destination):
        self.tweeter = tweeter
        self.queries = queries
        self.origin = origin
        self.destination = destination

    def do_it(self):
        services = list(self.queries.services_between(self.origin, self.destination))

        self.tweet_digest(services)
        self.direct_messages(services)

    @staticmethod
    def get_emoji(ser):
        if ser["etd"].lower() == "cancelled":
            return emoji_cross
        if ser["etd"].lower() == "on time":
            return emoji_tick
        else:
            return emoji_late

    @staticmethod
    def etd_str(ser):
        if ser["etd"].lower() == "cancelled" or ser["etd"].lower() == "on time":
            return ""
        else:
            return ser["etd"]

    @staticmethod
    def destination_str(ser):
        return ser["destination"][:10].strip()

    def tweet_digest(self, services):
        lines = map(lambda ser: "{0} {1} {2} {3}".format(self.get_emoji(ser),
                                                         ser["std"],
                                                         self.destination_str(ser),
                                                         self.etd_str(ser)),
                    services)

        message = "{0} {1} - {2}: \n".format(emoji_train, self.origin, self.destination)

        if len(lines) == 0:
            message += "\nNo services"

        for line in lines:
            if len(message) + len(line) > 140:
                break
            message = message + "\n" + line

        print message
        self.tweeter.tweet(message)

    def direct_messages(self, services):
        cancellations = filter(lambda x: x["etd"].lower() == "cancelled", services)
        for service in cancellations:
            message = "{0} {1} from {2} to {3} has been cancelled".format(
                emoji_skull,
                service["std"],
                service["origin"],
                service["destination"]
            )
            self.tweeter.message("DanteLore", message)


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
    rt = RailTweeter(twitter, queries, origin="PAD", destination="THA")
    rt.do_it()
