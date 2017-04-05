import unittest

import agrf_feed
from agrf_feed.apps import AgrfFeedConfig


# We don't need a database, so we choose to extend the unit test test case
class TestAgrfFeedConfig(unittest.TestCase):
    def setUp(self):
        self.agrf_feed_config = AgrfFeedConfig('test case', agrf_feed)
        self.agrf_feed_config.ready()

    def test_server_locations(self):
        locations = self.agrf_feed_config.get_server_locations()
        self.assertTrue(len(locations) == 2)

    def test_open_id_servers(self):
        locations = self.agrf_feed_config.get_server_locations()
        for location in locations:
            open_id_url = self.agrf_feed_config.get_openid_server(location)
            self.assertTrue(open_id_url)
            open_id_url.endswith('xrd.jsp')

    def test_dm_servers(self):
        locations = self.agrf_feed_config.get_server_locations()
        for location in locations:
            dm_server_url = self.agrf_feed_config.get_dm_server(location)
            self.assertTrue(dm_server_url)
            self.assertTrue(dm_server_url.endswith('datamanager'))
