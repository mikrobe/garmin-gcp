import argparse
import logging

from models import activity


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


def hello_gcs(event, context):
    """Background Cloud Function to be triggered by Cloud Storage.
       This generic function logs relevant data when a file is changed.

    Args:
        event (dict):  The dictionary with data specific to this type of event.
                       The `data` field contains a description of the event in
                       the Cloud Storage `object` format described here:
                       https://cloud.google.com/storage/docs/json_api/v1/objects#resource
        context (google.cloud.functions.Context): Metadata of triggering event.
    Returns:
        None; the output is written to Stackdriver Logging
    """

    print('Event ID: {}'.format(context.event_id))
    print('Event type: {}'.format(context.event_type))
    print('Bucket: {}'.format(event['bucket']))
    print('File: {}'.format(event['name']))
    print('Metageneration: {}'.format(event['metageneration']))
    print('Created: {}'.format(event['timeCreated']))
    print('Updated: {}'.format(event['updated']))


def import_daily_heart_rate(event, context):
    print("""This Function was triggered by messageId {} published at {}
    """.format(context.event_id, context.timestamp))


def command_feed(args):
    print("feed")


def command_export(args):
    print("export")


def command_load(args):
    activity.load(args.file, args.session_table_id, args.record_table_id)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--debug", action='store_true', help="Enables more detailed messages")

    garmin_parser = argparse.ArgumentParser(description="Garmin credentials parser", add_help=False)
    garmin_parser.add_argument("--username", "-u", required=True, help="Garmin Connect account name")
    garmin_parser.add_argument("--password", "-p", required=True, help="Garmin Connect account password")
    garmin_parser.add_argument("--cookie-jar", default=".garmin-cookies.txt", help="Filename with authentication cookies")

    subparsers = parser.add_subparsers(title="Commands")

    parser_feed = subparsers.add_parser("feed", parents=[garmin_parser], description="Feed activities from Garmin Connect")
    parser_feed.set_defaults(func=command_feed)

    parser_export = subparsers.add_parser("export", parents=[garmin_parser], description="Export activity file from Garmin Connect to GCS")
    parser_export.add_argument("--activity-id", help="Activity identifier")
    parser_export.set_defaults(func=command_export)

    parser_load = subparsers.add_parser("load", description="Load activity into BigQuery")
    parser_load.add_argument("--file", help="Activity file")
    parser_load.add_argument("--session-table-id", help="BigQuery session table")
    parser_load.add_argument("--record-table-id", help="BigQuery record table")
    parser_load.set_defaults(func=command_load)

    args = parser.parse_args()

    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=logging_level)

    args.func(args)


if __name__ == "__main__":
    main()
