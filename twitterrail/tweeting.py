from twitter import Twitter, OAuth


class MockTweeterApi:
    def __init__(self):
        self.tweets = []
        self.messages = []

    def tweet(self, message):
        self.tweets.append(message)

    def message(self, user, message):
        self.messages.append({"user": user, "message": message})


class RealTweeterApi:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.twitter = Twitter(
            auth=OAuth(access_token, access_token_secret, consumer_key, consumer_secret)
        )

    def tweet(self, message):
        self.twitter.statuses.update(status=message)

    def message(self, user, message):
        self.twitter.direct_messages.new(user=user, text=message)
