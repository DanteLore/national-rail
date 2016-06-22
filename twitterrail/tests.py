import unittest

from freezegun import freeze_time
from datetime import datetime
from queries import MockQueries
from tweeting import MockTweeterApi
from twitterrail.railtweeter import RailTweeter, emoji_cross, emoji_tick, emoji_train, emoji_late, emoji_skull


class TweetRailTests(unittest.TestCase):
    # Test the direct messaging service
    def test_do_not_duplicate_messages(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'11:18',
             'etd': u'Cancelled'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA", "Fred")
        rt.do_it()
        rt.do_it()
        rt.do_it()
        self.assertEqual(len(tweeter.messages), 1)
        assert {
                   "user": "Fred",
                   "timestamp": datetime.now(),
                   "message": "{0} 11:18 from London Paddington to Bedwyn has been cancelled".format(emoji_skull)
               } in tweeter.messages


    def test_dm_goes_to_correct_users(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'11:18',
             'etd': u'Cancelled'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA", "Bob,Geoff")
        rt.do_it()
        self.assertEqual(len(tweeter.messages), 2)
        assert {
                   "user": "Bob",
                   "timestamp": datetime.now(),
                   "message": "{0} 11:18 from London Paddington to Bedwyn has been cancelled".format(emoji_skull)
               } in tweeter.messages
        assert {
                   "user": "Geoff",
                   "timestamp": datetime.now(),
                   "message": "{0} 11:18 from London Paddington to Bedwyn has been cancelled".format(emoji_skull)
               } in tweeter.messages

    @freeze_time("2016-06-17 17:00:00")
    def test_dm_on_cancellation(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'11:18',
             'etd': u'Cancelled'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA", "Fred")
        rt.do_it()
        self.assertEqual(len(tweeter.messages), 1)
        assert {
                   "user": "Fred",
                   "timestamp": datetime.now(),
                   "message": "{0} 11:18 from London Paddington to Bedwyn has been cancelled".format(emoji_skull)
               } in tweeter.messages

    @freeze_time("2016-06-17 10:00:00")
    def test_dm_on_long_delay(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'11:18',
             'etd': u'11:45'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA", "Fred")
        rt.do_it()
        self.assertEqual(len(tweeter.messages), 1)
        assert {
                   "user": "Fred",
                   "timestamp": datetime.now(),
                   "message": "{0} 11:18 from London Paddington to Bedwyn delayed expected 11:45".format(emoji_late)
               } in tweeter.messages

    @freeze_time("2016-06-17 10:00:00")
    def test_no_dm_on_short_delay(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'17:18',
             'etd': u'17:22'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA", "Fred")
        rt.do_it()
        self.assertEqual(len(tweeter.messages), 0)

    @freeze_time("2016-06-18 17:00:00")
    def test_no_messages_on_weekends(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'17:18',
             'etd': u'Cancelled'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA", "Fred")
        rt.do_it()
        self.assertEqual(len(tweeter.messages), 0)

    @freeze_time("2016-06-17 06:00:00", tz_offset=-1)
    def test_no_messages_too_early(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'17:18',
             'etd': u'Cancelled'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA", "Fred")
        rt.do_it()
        self.assertEqual(len(tweeter.messages), 0)

    @freeze_time("2016-06-17 22:00:00")
    def test_no_messages_too_late(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'17:18',
             'etd': u'Cancelled'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA", "Fred")
        rt.do_it()
        self.assertEqual(len(tweeter.messages), 0)

    @freeze_time("2016-01-01 07:00:00")
    def test_no_messages_if_no_cancellations(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'11:18',
             'etd': u'On time'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA", "Fred")
        rt.do_it()
        self.assertEqual(len(tweeter.messages), 0)

    # Test the "Twitter Digest"
    @freeze_time("2016-01-01 07:00:00")
    def test_no_services(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[])
        rt = RailTweeter(tweeter, queries, "PAD", "THA", "Fred")
        rt.do_it()
        tweet = tweeter.tweets[0]
        assert "{0} PAD - THA".format(emoji_train) in tweet
        assert "No services" in tweet

    @freeze_time("2016-01-01 07:00:00")
    def test_normal_train(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'11:18',
             'etd': u'On time'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA", "Fred")
        rt.do_it()
        tweet = tweeter.tweets[0]
        assert "{0} PAD - THA".format(emoji_train) in tweet
        assert "{0} 11:18 Bedwyn".format(emoji_tick) in tweet

    @freeze_time("2016-01-01 07:00:00")
    def test_cancelled_train(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'11:18',
             'etd': u'Cancelled'},
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'12:18',
             'etd': u'On time'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA", "Fred")
        rt.do_it()
        tweet = tweeter.tweets[0]
        assert "{0} PAD - THA".format(emoji_train) in tweet
        assert "{0} 11:18 Bedwyn".format(emoji_cross) in tweet
        assert "{0} 12:18 Bedwyn".format(emoji_tick) in tweet

    @freeze_time("2016-01-01 07:00:00")
    def test_late_train(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'Bedwyn', 'platform': '-', 'std': u'11:18', 'etd': u'11:24'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA", "Fred")
        rt.do_it()
        tweet = tweeter.tweets[0]
        self.assertTrue("{0} PAD - THA".format(emoji_train) in tweet)
        self.assertTrue("{0} 11:18 Bedwyn 11:24".format(emoji_late) in tweet)

    @freeze_time("2016-01-01 07:00:00")
    def test_long_station_names_cropped_at_ten_chars(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'This is a very long station name', 'platform': '-',
             'std': u'11:18', 'etd': u'On time'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA", "Fred")
        rt.do_it()
        tweet = tweeter.tweets[0]
        self.assertTrue("{0} PAD - THA".format(emoji_train) in tweet)
        self.assertTrue("{0} 11:18 This is a".format(emoji_tick) in tweet)

    @freeze_time("2016-01-01 07:00:00")
    def test_tweet_cropped_at_140_chars(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'origin': 'London Paddington', 'destination': u'Station 1', 'platform': '-', 'std': u'01:18',
             'etd': u'On time'},
            {'origin': 'London Paddington', 'destination': u'Station 2', 'platform': '-', 'std': u'02:18',
             'etd': u'On time'},
            {'origin': 'London Paddington', 'destination': u'Station 3', 'platform': '-', 'std': u'03:18',
             'etd': u'On time'},
            {'origin': 'London Paddington', 'destination': u'Station 4', 'platform': '-', 'std': u'04:18',
             'etd': u'On time'},
            {'origin': 'London Paddington', 'destination': u'Station 5', 'platform': '-', 'std': u'05:18',
             'etd': u'On time'},
            {'origin': 'London Paddington', 'destination': u'Station 6', 'platform': '-', 'std': u'06:18',
             'etd': u'On time'}
        ])
        rt = RailTweeter(tweeter, queries, "PAD", "THA", "Fred")
        rt.do_it()
        tweet = tweeter.tweets[0]
        self.assertTrue("{0} PAD - THA".format(emoji_train) in tweet)
        self.assertFalse("06:18" in tweet)

    @freeze_time("2016-01-01 07:00:00")
    def test_home_to_work_in_the_morning(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[])
        rt = RailTweeter(tweeter, queries, "THA", "PAD", "Fred")
        rt.do_it()
        tweet = tweeter.tweets[0]
        assert "{0} THA - PAD".format(emoji_train) in tweet

    @freeze_time("2016-01-01 13:00:00")
    def test_home_to_work_in_the_morning(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[])
        rt = RailTweeter(tweeter, queries, "THA", "PAD", "Fred")
        rt.do_it()
        tweet = tweeter.tweets[0]
        assert "{0} PAD - THA".format(emoji_train) in tweet
