import argparse
import datetime
import logging
from google.cloud import bigquery

from functions.garmin.garminclient import GarminClient
from functions.models.heartrate import HeartRate


def hello_world(event, context):
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    """
    import base64

    print("""This Function was triggered by messageId {} published at {}
    """.format(context.event_id, context.timestamp))

    if 'data' in event:
        name = base64.b64decode(event['data']).decode('utf-8')
    else:
        name = 'World'
    print('Hello {}!'.format(name))


def import_daily_heart_rate(event, context):
    print("""This Function was triggered by messageId {} published at {}
    """.format(context.event_id, context.timestamp))


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--date", "-d", required=True, type=datetime.date.fromisoformat)
    parser.add_argument("--username", "-u", required=True, help="Garmin Connect account username")
    parser.add_argument("--password", "-p", required=True, help="Garmin Connect account password")
    parser.add_argument("--cookie-jar", default=".garmin-cookies.txt", help="Filename with authentication cookies")
    parser.add_argument("--debug", action='store_true', help="Enables more detailed messages")

    args = parser.parse_args()

    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=logging_level)

    bq_client = bigquery.Client()
    table_id = "garmin-267619.wellness.heart_rate"

    with _garmin_client(args) as connection:
        heart_rate_data = connection.get_daily_heart_rate(args.username, args.date)
        heart_rate = HeartRate(heart_rate_data)
        heart_rate_values = heart_rate.heart_rate_values()
        print(heart_rate_values)

        # errors = bq_client.insert_rows_json(table_id, heart_rate_values)
        # if errors == []:
        #     print("New rows have been added.")
        # else:
        #     print("Encountered errors while inserting rows: {}".format(errors))


def _garmin_client(args):
    return GarminClient(username=args.username, password=args.password, cookie_jar=args.cookie_jar)


if __name__ == "__main__":
    main()
