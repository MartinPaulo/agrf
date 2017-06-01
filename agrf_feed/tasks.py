import os
import time

from billiard.exceptions import SoftTimeLimitExceeded
from celery import shared_task
from celery.utils.log import get_task_logger
from genomespaceclient import GenomeSpaceClient
from genomespaceclient.exceptions import GSClientException

from agrf_feed.models import FileDescriptor

logging = get_task_logger(__name__)


# Set the time limit for this task to two hours...
@shared_task(time_limit=7200)
def celery_move_files(chosen_files, target_dir, token):
    client = GenomeSpaceClient(token=token)
    # common prefix doesn't return the common path: but rather
    # all the characters that match. So we need to trim it back to the path
    # separator...
    base = os.path.commonprefix(chosen_files).rpartition(os.sep)[0]
    for path in chosen_files:
        # there will always be a leading '/', as the base doesn't include it
        # so remove it from the file name
        file_name = path[len(base) + 1 if len(base) else 0:]
        # the genomespace will expect a '/' in a file name to be a directory
        file_name = file_name.replace('/', '_')
        bucket = target_dir['url'] + '/' + file_name
        fd = FileDescriptor.get_file_descriptor_for(path)
        try:
            logging.info('About to move %s' % path)
            start_time = time.time()
            client.copy(path, bucket)
            elapsed_time = time.time() - start_time
            bytes_moved = os.path.getsize(path)
            logging.info(
                '%s bytes moved in %.2f seconds' % (bytes_moved, elapsed_time))
        except GSClientException as error:
            logging.error('Error uploading %s: %s' % (file_name, error))
            fd.set_failed_upload()
        except SoftTimeLimitExceeded:
            logging.error('Soft time limit exceed for %s' % path)
            fd.set_failed_upload()
        else:
            logging.info('Successfully uploaded %s' % file_name)
            fd.set_uploaded()
        fd.save()
