import logging

from google.cloud import storage


class GcsClient(object):
    _LOG = logging.getLogger(__name__)

    def __init__(self):
        self.client = storage.Client()

    def download(self, bucket, name, destination_file):
        self._LOG.info("Download %s/%s into %s", bucket, name, destination_file)
        bucket = self.client.get_bucket(bucket)
        blob = bucket.get_blob(name)
        blob.download_to_filename(destination_file)

