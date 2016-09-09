import argparse
import logging
from time import sleep

from twitterrail.queries import RealQueries
from twitterrail.railtweeter import RailTweeter
from twitterrail.tweeting import RealTweeterApi

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tweeting about railways')
    parser.add_argument('--home', help='Home station CRS (default "THA")', default="THA")
    parser.add_argument('--work', help='Work station CRS (default "PAD")', default="PAD")
    parser.add_argument('--users', help='Users to DM (comma separated)', default="")
    parser.add_argument('--forever', help='Use this switch to run the script forever (once ever 5 mins)', action='store_true', default=False)
    parser.add_argument('--rail-key', help='API Key for National Rail', required=True)
    parser.add_argument('--consumer-key', help='Consumer Key for Twitter', required=True)
    parser.add_argument('--consumer-secret', help='Consumer Secret for Twitter', required=True)
    parser.add_argument('--access-token', help='Access Token for Twitter', required=True)
    parser.add_argument('--access-token-secret', help='Access Token Secret for Twitter', required=True)
    parser.add_argument('--log-level', help='Log level to use. Default=INFO', default="INFO")
    args = parser.parse_args()

    logger = logging.getLogger("JiraBot")
    logger.setLevel(args.log_level)
    logger.addHandler(logging.StreamHandler())

    twitter = RealTweeterApi(args.consumer_key, args.consumer_secret, args.access_token, args.access_token_secret)
    queries = RealQueries("http://lite.realtime.nationalrail.co.uk/OpenLDBWS/ldb9.asmx", args.rail_key)
    rt = RailTweeter(twitter, queries, home=args.home, work=args.work, users=args.users, logger=logger)

    while True:
        try:
            rt.do_it()
        except Exception as e:
            logger.exception("I crashed")
        if not args.forever:
            break
        sleep(300)
