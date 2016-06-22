from twitter import Twitter, OAuth
from datetime import datetime

class MockTweeterApi:
    def __init__(self):
        self.tweets = []
        self.messages = []

    def tweet(self, message):
        self.tweets.append(message)

    def messages_sent_to(self, user):
        user_messages = filter(lambda msg: msg["user"] == user, self.messages)
        return user_messages

    def message(self, user, message):
        self.messages.append({"user": user, "message": message, "timestamp": datetime.now()})


class RealTweeterApi:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.twitter = Twitter(
            auth=OAuth(access_token, access_token_secret, consumer_key, consumer_secret)
        )

    def tweet(self, message):
        self.twitter.statuses.update(status=message)

    def messages_sent_to(self, user):
        dms = map(lambda msg: {
            "user": msg["recipient"]["screen_name"],
            "timestamp": datetime.strptime(msg["created_at"], '%a %b %d %H:%M:%S +0000 %Y'),
            "message": msg["text"]
        }, self.twitter.direct_messages.sent(count=100, include_rts=1))
        user_messages = filter(lambda msg: msg["user"] == user, dms)
        return user_messages

    def message(self, user, message):
        self.twitter.direct_messages.new(user=user, text=message)
