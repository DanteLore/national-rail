import unittest
from queries import MockQueries
from tweeting import MockTweeterApi
from twitterrail import RailTweeter


class TweetRailTests(unittest.TestCase):
    def test_direct_trains_from_paddington_to_thatcham_are_tweeted(self):
        tweeter = MockTweeterApi()
        queries = MockQueries(services=[
            {'destination': u'Bedwyn', 'platform': '-', 'std': u'11:18', 'etd': u'Cancelled'},
            {'destination': u'Bedwyn', 'platform': '-', 'std': u'12:18', 'etd': u'On time'}]
        )
        rt = RailTweeter(tweeter, queries)
        rt.do_it()
        tweet = tweeter.tweets[0]
        self.assertTrue("11:18 Bedwyn Cancelled" in tweet)
        self.assertTrue("12:18 Bedwyn On time" in tweet)
