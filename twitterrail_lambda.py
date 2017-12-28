import logging
import boto3
import os
from base64 import b64decode

from twitterrail.queries import Queries
from twitterrail.railtweeter import RailTweeter
from twitterrail.tweeting import TweeterApi


def decrypt_env(name):
    encrypted = os.environ[name]
    return boto3.client('kms').decrypt(CiphertextBlob=b64decode(encrypted))['Plaintext']


def lambda_handler(event, context):
    home = os.environ['HOME']
    work = os.environ['WORK']
    users = os.environ['USERS']

    consumer_key = decrypt_env('CONSUMER_KEY')
    consumer_secret = decrypt_env('CONSUMER_SECRET')
    access_token = decrypt_env('ACCESS_TOKEN')
    access_token_secret = decrypt_env('ACCESS_TOKEN_SECRET')
    rail_key = decrypt_env('RAIL_KEY')

    logger = logging.getLogger("TwitterRail")
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    logger.setLevel("INFO")
    logger.addHandler(streamHandler)

    twitter = TweeterApi(consumer_key, consumer_secret, access_token, access_token_secret)
    queries = Queries("http://lite.realtime.nationalrail.co.uk/OpenLDBWS/ldb9.asmx", rail_key)
    rt = RailTweeter(twitter, queries, home=home, work=work, users=users, logger=logger)
    rt.do_it()

    return "done"
