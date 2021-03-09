import dataclasses
import itertools
import os
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime

import pytz
from fitdecode import FitDataMessage
from fitdecode import FitReader

from garmin.garminclient import GarminClient
from gcp.bigqueryclient import BigQueryClient
from gcp.firestoreclient import FirestoreClient
from gcp.gcsclient import GcsClient
from models.fitdata import FitData


@dataclass
class Session(FitData):
    activity_id: str = None
    timestamp: datetime = None
    nec_lat: int = None
    nec_long: int = None
    swc_lat: int = None
    swc_long: int = None
    avg_cadence: int = None
    avg_heart_rate: int = None
    avg_power: int = None
    avg_speed: float = None
    avg_temperature: int = None
    max_cadence: int = None
    max_heart_rate: int = None
    max_power: int = None
    max_speed: float = None
    max_temperature: int = None
    total_ascent: int = None
    total_calories: int = None
    total_descent: int = None
    total_distance: float = None
    total_elapsed_time: float = None
    total_timer_time: float = None


@dataclass
class Record(FitData):
    activity_id: str = None
    timestamp: datetime = None
    position_lat: int = None
    position_long: int = None
    altitude: float = None
    cadence: int = None
    heart_rate: int = None
    power: int = None
    speed: float = None
    temperature: int = None


def feed(garmin_username, garmin_password, cookie_jar, activity_table):
    bq_client = BigQueryClient()
    fs_client = FirestoreClient()

    with GarminClient(garmin_username, garmin_password, cookie_jar) as garmin_client:
        activities_json = garmin_client.get_activities(limit=10)
        activities = map(lambda x: _parse_json(x), activities_json)
        new_activities = itertools.takewhile(lambda x: not fs_client.is_exits("activity", x["id"]), activities)
        bq_client.insert_rows(activity_table, activities)


def export(garmin_username, garmin_password, cookie_jar, activity_id, activity_bucket):
    gcs_client = GcsClient()
    zip_filename = "{}.zip".format(activity_id)
    fit_filename = "{}.fit".format(activity_id)

    with GarminClient(garmin_username, garmin_password, cookie_jar) as garmin_client:
        with tempfile.TemporaryDirectory() as temp_dir:
            local_file = os.path.join(temp_dir, zip_filename)
            garmin_client.download_activity(activity_id, local_file)
            archive = zipfile.ZipFile(local_file)
            original_fit_filename = next(x for x in archive.namelist() if x.lower().endswith(".fit"))
            archive.extract(original_fit_filename, path=temp_dir)
            gcs_client.upload(activity_bucket, fit_filename, os.path.join(temp_dir, original_fit_filename))


def load(gcs_bucket, gcs_object, session_table, record_table):
    gcs_client = GcsClient()
    bq_client = BigQueryClient()

    activity_id = os.path.splitext(os.path.basename(gcs_object))[0]

    with tempfile.TemporaryDirectory() as temp_dir:
        local_file = os.path.join(temp_dir, gcs_object)
        gcs_client.download(gcs_bucket, gcs_object, local_file)

        records = _parse_fit_records(local_file, activity_id)
        bq_client.insert_rows(record_table, records)

        sessions = _parse_fit_sessions(local_file, activity_id)
        bq_client.insert_rows(session_table, sessions)


def _parse_fit_frame(file, frame_name):
    with FitReader(file) as fit:
        for frame in fit:
            if isinstance(frame, FitDataMessage):
                if frame.name == frame_name:
                    yield frame


def _parse_fit_records(file, activity_id):
    for frame in _parse_fit_frame(file, 'record'):
        record = Record(activity_id=activity_id)
        record.parse(frame)
        yield dataclasses.asdict(record)


def _parse_fit_sessions(file, activity_id):
    for frame in _parse_fit_frame(file, 'session'):
        session = Session(activity_id=activity_id)
        session.parse(frame)
        yield dataclasses.asdict(session)


def _parse_json(json):
    timestamp = datetime.strptime(json['startTimeGMT'], '%Y-%m-%d %H:%M:%S')
    timestamp_utc = timestamp.replace(tzinfo=pytz.UTC)

    return {
        "timestamp": timestamp_utc,
        "id": json['activityId'],
        "name": json['activityName'],
        "description": json['description'],
        "type": json['activityType']['typeKey']
    }
