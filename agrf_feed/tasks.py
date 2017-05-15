import html
import logging
import os

from celery import shared_task
from genomespaceclient import GenomeSpaceClient
from genomespaceclient.exceptions import GSClientException


@shared_task
def celery_move_files(chosen_files, target_dir, token):
    client = GenomeSpaceClient(token=token)
    for escaped_path in chosen_files:
        path = html.unescape(escaped_path)
        file_name = os.path.basename(path)
        bucket = target_dir['url'] + '/' + file_name
        try:
            client.copy(path, bucket)
        except GSClientException as error:
            message = """Error uploading %s: %s""" % (file_name, error)
            # messages.add_message(request, messages.ERROR, message)
            logging.error(message)
        else:
            message = """Successfully uploaded %s""" % file_name
            # messages.add_message(request, messages.INFO, message)
            logging.info(message)
            # Remove our list of files to upload from the session
