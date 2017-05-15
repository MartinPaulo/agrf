from .celery import celery_app as celery_app

default_app_config = 'agrf_feed.apps.AgrfFeedConfig'

__all__ = ['celery_app']
