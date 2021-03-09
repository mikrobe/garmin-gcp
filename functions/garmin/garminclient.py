import http
import json
import logging
import os
import re
import sys

import requests


class GarminClient(object):
    _SSO_LOGIN_URL = "https://sso.garmin.com/sso/signin"
    _ACTIVITY_LIST_SERVICE_URL = "https://connect.garmin.com/modern/proxy/activitylist-service"
    _DOWNLOAD_SERVICE_URL = "https://connect.garmin.com/proxy/download-service/"

    _REQUIRED_HEADERS = {
        "Referer": "https://connect.garmin.com/modern/workouts",
        "nk": "NT"
    }

    _LOG = logging.getLogger(__name__)

    def __init__(self, username, password, cookie_jar):
        self.username = username
        self.password = password
        self.cookie_jar = cookie_jar
        self.session = None

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._disconnect()

    def get_activities(self, batch_size=10, limit=sys.maxsize):
        assert self.session

        request = "{}/activities/search/activities".format(GarminClient._ACTIVITY_LIST_SERVICE_URL)
        for start_index in range(0, limit, batch_size):
            params = {
                "start": start_index,
                "limit": batch_size,
            }

            self._LOG.info("Get activities, start: %d, limit: %d", start_index, batch_size)

            response = self.session.get(request, params=params, headers=GarminClient._REQUIRED_HEADERS)
            response.raise_for_status()

            response_jsons = json.loads(response.text)
            if not response_jsons or response_jsons == []:
                break

            for response_json in response_jsons:
                yield response_json

    def download_activity(self, activity_id, file, chunk_size=1024):
        assert self.session

        self._LOG.info("Get activity '%s'", activity_id),

        response = self.session.get("{}/files/activity/{}".format(GarminClient._DOWNLOAD_SERVICE_URL, activity_id), stream=True)
        response.raise_for_status()

        with open(file, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=chunk_size):
                fd.write(chunk)

    def _connect(self):
        self.session = requests.Session()
        self.session.cookies = http.cookiejar.LWPCookieJar(self.cookie_jar)

        if os.path.isfile(self.cookie_jar):
            self.session.cookies.load(ignore_discard=True, ignore_expires=True)

        response = self.session.get("https://connect.garmin.com/modern/settings", allow_redirects=False)
        if response.status_code != 200:
            self._LOG.info("Authenticate user '%s'", self.username)
            self._authenticate()
        else:
            self._LOG.info("User '%s' already authenticated", self.username)

    def _disconnect(self):
        if self.session:
            self.session.cookies.save(ignore_discard=True, ignore_expires=True)
            self.session.close()
            self.session = None

    def _authenticate(self):
        assert self.session

        form_data = {
            "username": self.username,
            "password": self.password,
            "embed": "false"
        }
        request_params = {
            "service": "https://connect.garmin.com/modern"
        }
        headers = {'origin': 'https://sso.garmin.com'}

        auth_response = self.session.post(
            GarminClient._SSO_LOGIN_URL, headers=headers, params=request_params, data=form_data)
        auth_response.raise_for_status()

        auth_ticket_url = self._extract_auth_ticket_url(auth_response.text)

        response = self.session.get(auth_ticket_url)
        response.raise_for_status()

    @staticmethod
    def _extract_auth_ticket_url(auth_response):
        match = re.search(r'response_url\s*=\s*"(https:[^"]+)"', auth_response)
        if not match:
            raise Exception("Unable to extract auth ticket URL from:\n%s" % auth_response)
        auth_ticket_url = match.group(1).replace("\\", "")
        return auth_ticket_url
