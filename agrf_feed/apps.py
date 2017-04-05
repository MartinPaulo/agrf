import requests
from django.apps import AppConfig

KEY_DM_SERVER = "prod.dmServer"
KEY_OPEN_ID = 'prod.openIdUrl'

URLS = {
    # The permanent location of file containing international GS server urls.
    'genomespace.org': 'https://dm.genomespace.org/config/v1.0/serverurl.properties',
    # The location of file containing australian GS server urls.
    'genomespace.au': 'https://genomespace.genome.edu.au/config/v1.0/serverurl.properties'
}


class AgrfFeedConfig(AppConfig):
    name = 'agrf_feed'

    _urls_openid = {}
    _urls_dm = {}

    @staticmethod
    def _get_key_value(key, lines, default=None):
        for line in lines:
            if line.startswith("%s" % key):
                return line.split("=")[1]
        return default

    @classmethod
    def _get_server_urls(cls, location, source_url):
        r = requests.get(source_url)
        if r.status_code == requests.codes.ok:
            lines = r.text.split('\n')
            cls._urls_openid[location] = cls._get_key_value(KEY_OPEN_ID, lines)
            cls._urls_dm[location] = cls._get_key_value(KEY_DM_SERVER, lines)

    @classmethod
    def _get_urls(cls):
        for location, value in URLS.items():
            cls._get_server_urls(location, value)
            cls._get_server_urls(location, value)

    @classmethod
    def get_server_locations(cls):
        """ :return: a list containing the server locations """
        return list(URLS.keys())

    @classmethod
    def get_dm_server(cls, location):
        """
        :param location: the location of the GenomeSpace server
        :return: the dm server url that matches the location argument
        """
        return cls._urls_dm[location]

    @classmethod
    def get_openid_server(cls, location):
        """
        :param location: the location of the GenomeSpace server
        :return: the dm server url that matches the location argument
        """
        return cls._urls_openid[location]

    # https://docs.djangoproject.com/en/1.11/ref/applications/#django.apps.AppConfig.ready
    def ready(self):
        self._get_urls()
