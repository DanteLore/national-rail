import unittest
from queries import MockQueries
from tweeting import MockTweeterApi
from twitterrail import RailTweeter, emoji_cross, emoji_tick, emoji_train, emoji_late


class TweetRailTests(unittest.TestCase):
    def test_no_services(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[])
        rt = RailTweeter(tweeter, queries, "PAD", "THA")
        rt.do_it()
        tweet = tweeter.tweets[0]
        self.assertTrue("{0} PAD - THA".format(emoji_train) in tweet)
        self.assertTrue("No services" in tweet)

    def test_normal_train(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'destination': u'Bedwyn', 'platform': '-', 'std': u'11:18', 'etd': u'On time'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA")
        rt.do_it()
        tweet = tweeter.tweets[0]
        self.assertTrue("{0} PAD - THA".format(emoji_train) in tweet)
        self.assertTrue("{0} 11:18 Bedwyn".format(emoji_tick) in tweet)

    def test_cancelled_train(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'destination': u'Bedwyn', 'platform': '-', 'std': u'11:18', 'etd': u'Cancelled'},
            {'destination': u'Bedwyn', 'platform': '-', 'std': u'12:18', 'etd': u'On time'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA")
        rt.do_it()
        tweet = tweeter.tweets[0]
        self.assertTrue("{0} PAD - THA".format(emoji_train) in tweet)
        self.assertTrue("{0} 11:18 Bedwyn".format(emoji_cross) in tweet)
        self.assertTrue("{0} 12:18 Bedwyn".format(emoji_tick) in tweet)

    def test_late_train(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'destination': u'Bedwyn', 'platform': '-', 'std': u'11:18', 'etd': u'11:24'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA")
        rt.do_it()
        tweet = tweeter.tweets[0]
        self.assertTrue("{0} PAD - THA".format(emoji_train) in tweet)
        self.assertTrue("{0} 11:18 Bedwyn 11:24".format(emoji_late) in tweet)

    def test_long_station_names_cropped_at_ten_chars(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'destination': u'This is a very long station name', 'platform': '-', 'std': u'11:18', 'etd': u'On time'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA")
        rt.do_it()
        tweet = tweeter.tweets[0]
        self.assertTrue("{0} PAD - THA".format(emoji_train) in tweet)
        self.assertTrue("{0} 11:18 This is a".format(emoji_tick) in tweet)

    def test_tweet_cropped_at_140_chars(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'destination': u'Station 1', 'platform': '-', 'std': u'01:18', 'etd': u'On time'},
            {'destination': u'Station 2', 'platform': '-', 'std': u'02:18', 'etd': u'On time'},
            {'destination': u'Station 3', 'platform': '-', 'std': u'03:18', 'etd': u'On time'},
            {'destination': u'Station 4', 'platform': '-', 'std': u'04:18', 'etd': u'On time'},
            {'destination': u'Station 5', 'platform': '-', 'std': u'05:18', 'etd': u'On time'},
            {'destination': u'Station 6', 'platform': '-', 'std': u'06:18', 'etd': u'On time'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA")
        rt.do_it()
        tweet = tweeter.tweets[0]
        self.assertTrue("{0} PAD - THA".format(emoji_train) in tweet)
        self.assertFalse("06:18" in tweet)
