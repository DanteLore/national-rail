import argparse
from time import sleep

from twitterrail.queries import RealQueries
from twitterrail.railtweeter import RailTweeter
from twitterrail.tweeting import RealTweeterApi

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tweeting about railways')
    parser.add_argument('--rail-key', help='API Key', required=True)
    parser.add_argument('--consumer-key', help='Consumer Key', required=True)
    parser.add_argument('--consumer-secret', help='Consumer Secret', required=True)
    parser.add_argument('--access-token', help='Access Token', required=True)
    parser.add_argument('--access-token-secret', help='Access Token Secret', required=True)
    parser.add_argument('--url', help='API URL', default="http://lite.realtime.nationalrail.co.uk/OpenLDBWS/ldb9.asmx")
    parser.add_argument('--users', help='Users to DM (comma separated)', default="ThatchamTrains")
    parser.add_argument('--forever', help='Use this switch to run the script forever (once ever 5 mins)', action='store_true', default=False)
    args = parser.parse_args()

    twitter = RealTweeterApi(args.consumer_key, args.consumer_secret, args.access_token, args.access_token_secret)
    queries = RealQueries(args.url, args.rail_key)
    rt = RailTweeter(twitter, queries, home="THA", work="PAD", users=args.users)

    while True:
        rt.do_it()
        if not args.forever:
            break
        sleep(300)
