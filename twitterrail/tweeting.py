import logging

from twitter import Twitter, OAuth, TwitterHTTPError
from datetime import datetime


class TweeterApi:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, logger=None):
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger("TESTING")
            self.logger.setLevel("DEBUG")
            self.logger.addHandler(logging.StreamHandler())

        self.twitter = Twitter(auth=OAuth(access_token, access_token_secret, consumer_key, consumer_secret))

    def tweet(self, message):
        try:
            self.twitter.statuses.update(status=message)
        except TwitterHTTPError as e:
            self.logger.exception("Failed to send tweet")

    def messages_sent_to(self, user):
        dms = map(lambda msg: {
            "user": msg["recipient"]["screen_name"],
            "timestamp": datetime.strptime(msg["created_at"], '%a %b %d %H:%M:%S +0000 %Y'),
            "message": msg["text"].encode('utf-8')
        }, self.twitter.direct_messages.sent(count=100, include_rts=1))
        user_messages = filter(lambda msg: msg["user"] == user, dms)
        return user_messages

    def message(self, user, message):
        try:
            self.twitter.direct_messages.new(user=user, text=message)
        except TwitterHTTPError as e:
            self.logger.exception("Failed to send direct message")
