import unittest

from queries import MockQueries
from tweeting import MockTweeterApi
from twitterrail import RailTweeter, emoji_cross, emoji_tick, emoji_train, emoji_late, emoji_skull


class TweetRailTests(unittest.TestCase):

    # Only DM on weekdays after 6am and before 10pm

    # Commands to "shush" DMs based on DMs received (for bank holidays and days off!)

    # Tweet and DM THA-PAD in the morning and PAD-THA after lunch

    # Set up a new twitter acct!

    # Find somewhere to run it!  Plug in a PI!

    # Test the direct messaging service
    def test_dm_on_cancellation(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'11:18', 'etd': u'Cancelled'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA")
        rt.do_it()
        self.assertEqual(len(tweeter.messages), 1)
        self.assertTrue(
                {
                    "user": "DanteLore",
                    "message": "{0} 11:18 from London Paddington to Bedwyn has been cancelled".format(emoji_skull)
                }
                in tweeter.messages)

    def test_no_messages_if_no_cancellations(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'11:18', 'etd': u'On time'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA")
        rt.do_it()
        self.assertEqual(len(tweeter.messages), 0)


    # Test the "Twitter Digest"
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
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'11:18', 'etd': u'On time'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA")
        rt.do_it()
        tweet = tweeter.tweets[0]
        self.assertTrue("{0} PAD - THA".format(emoji_train) in tweet)
        self.assertTrue("{0} 11:18 Bedwyn".format(emoji_tick) in tweet)

    def test_cancelled_train(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'11:18', 'etd': u'Cancelled'},
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'12:18', 'etd': u'On time'}
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
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'11:18', 'etd': u'11:24'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA")
        rt.do_it()
        tweet = tweeter.tweets[0]
        self.assertTrue("{0} PAD - THA".format(emoji_train) in tweet)
        self.assertTrue("{0} 11:18 Bedwyn 11:24".format(emoji_late) in tweet)

    def test_long_station_names_cropped_at_ten_chars(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'This is a very long station name', 'platform': '-', 'std': u'11:18', 'etd': u'On time'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA")
        rt.do_it()
        tweet = tweeter.tweets[0]
        self.assertTrue("{0} PAD - THA".format(emoji_train) in tweet)
        self.assertTrue("{0} 11:18 This is a".format(emoji_tick) in tweet)

    def test_tweet_cropped_at_140_chars(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'Station 1', 'platform': '-', 'std': u'01:18', 'etd': u'On time'},
            {'origin': 'London Paddington', 'destination': u'Station 2', 'platform': '-', 'std': u'02:18', 'etd': u'On time'},
            {'origin': 'London Paddington', 'destination': u'Station 3', 'platform': '-', 'std': u'03:18', 'etd': u'On time'},
            {'origin': 'London Paddington', 'destination': u'Station 4', 'platform': '-', 'std': u'04:18', 'etd': u'On time'},
            {'origin': 'London Paddington', 'destination': u'Station 5', 'platform': '-', 'std': u'05:18', 'etd': u'On time'},
            {'origin': 'London Paddington', 'destination': u'Station 6', 'platform': '-', 'std': u'06:18', 'etd': u'On time'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA")
        rt.do_it()
        tweet = tweeter.tweets[0]
        self.assertTrue("{0} PAD - THA".format(emoji_train) in tweet)
        self.assertFalse("06:18" in tweet)
