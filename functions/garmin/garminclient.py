import http
import json
import logging
import os
import re
import sys

import requests

# https://connect.garmin.com/modern/proxy/wellness-service/wellness/dailyStress/2021-02-12
# https://connect.garmin.com/modern/proxy/wellness-service/wellness/dailyMovement/mkuthan?calendarDate=2021-02-12
# https://connect.garmin.com/modern/proxy/wellness-service/wellness/dailySleepData/mkuthan?date=2021-02-12
# https://connect.garmin.com/modern/proxy/wellness-service/wellness/dailySummaryChart/mkuthan?date=2021-02-12

# https://github.com/felipeam86/garpy/blob/master/garpy/resources/default_config.yaml

class GarminClient(object):
    _SSO_LOGIN_URL = "https://sso.garmin.com/sso/signin"
    _WELLNESS_SERVICE_URL = "https://connect.garmin.com/modern/proxy/wellness-service"

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

    def get_daily_heart_rate(self, user, date):
        assert self.session

        date_formatted = date.strftime("%Y-%m-%d")
        request = "{}/wellness/dailyHeartRate/{}?date={}".format(GarminClient._WELLNESS_SERVICE_URL, user, date_formatted)

        response = self.session.get(request)
        response.raise_for_status()

        return json.loads(response.text)

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
