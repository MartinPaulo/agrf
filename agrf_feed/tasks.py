import html
import logging
import os

from celery import shared_task
from genomespaceclient import GenomeSpaceClient
from genomespaceclient.exceptions import GSClientException


@shared_task
def celery_move_files(chosen_files, target_dir, token):
    client = GenomeSpaceClient(token=token)
    files = [html.unescape(file) for file in chosen_files]
    # common prefix doesn't return the common path: but rather
    # all the characters that match. So we need to trim it back to the path
    # separator...
    base = os.path.commonprefix(files).rpartition(os.sep)[0]
    for path in files:
        # there will always be a leading '/', as the base doesn't include it
        # so remove it from the file name
        file_name = path[len(base) + 1 if len(base) else 0:]
        # the genomespace will expect a '/' in a file name to be a directory
        file_name = file_name.replace('/', '_')
        bucket = target_dir['url'] + '/' + file_name
        try:
            client.copy(path, bucket)
        except GSClientException as error:
            message = """Error uploading %s: %s""" % (file_name, error)
            logging.error(message)
        else:
            message = """Successfully uploaded %s""" % file_name
            logging.info(message)
