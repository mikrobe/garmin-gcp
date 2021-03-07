import os
from dataclasses import dataclass
from datetime import datetime

from fitdecode import FitReader, FitDataMessage

from gcp.bigqueryclient import BigQueryClient
from models.fitdata import FitData
from utils.dataclass import map_as_dict


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


@dataclass(frozen=True)
class Activity(object):
    sessions: [Session]
    records: [Record]

    @staticmethod
    def parse(activity_id, file):
        sessions = []
        records = []

        with FitReader(file) as fit:
            for frame in fit:
                if isinstance(frame, FitDataMessage):
                    if frame.name == 'session':
                        session = Session(activity_id=activity_id)
                        session.parse(frame)
                        sessions.append(session)
                    if frame.name == 'record':
                        record = Record(activity_id=activity_id)
                        record.parse(frame)
                        records.append(record)

        return Activity(
            sessions,
            records
        )


def load(file, session_table_id, record_table_id):
    activity_id = os.path.basename(file)
    activity = Activity.parse(activity_id, file)

    bq_client = BigQueryClient()
    bq_client.insert_rows(session_table_id, map_as_dict(activity.sessions))
    bq_client.insert_rows(record_table_id, map_as_dict(activity.records))
