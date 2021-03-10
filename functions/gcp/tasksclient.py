import logging

from google.cloud import tasks_v2


class TaskClient(object):
    _LOG = logging.getLogger(__name__)

    def __init__(self):
        self.client = tasks_v2.Client()
