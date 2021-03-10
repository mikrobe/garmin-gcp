import argparse
import logging
import os

from models import activity

logging.basicConfig(level=logging.INFO)


def function_feed(event, context):
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


def function_export(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'name' in request_json:
        name = request_json['name']
    elif request_args and 'name' in request_args:
        name = request_args['name']
    else:
        name = 'World'
    return 'Hello {}!'.format(name)


def function_load(event, context):
    gcs_bucket = event['bucket']
    gcs_object = event['name']

    session_table = os.environ['SESSION_TABLE']
    record_table = os.environ['RECORD_TABLE']

    activity.load(gcs_bucket, gcs_object, session_table, record_table)


def command_feed(args):
    activity.feed(args.username, args.password, args.cookie_jar, args.export_tasks_queue, args.activity_table)


def command_export(args):
    activity.export(args.username, args.password, args.cookie_jar, args.activity_id, args.gcs_bucket)


def command_load(args):
    activity.load(args.gcs_bucket, args.gcs_object, args.session_table, args.record_table)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--debug", action='store_true', help="Enables more detailed messages")

    garmin_parser = argparse.ArgumentParser(description="Garmin credentials parser", add_help=False)
    garmin_parser.add_argument("--username", "-u", required=True, help="Garmin Connect account name")
    garmin_parser.add_argument("--password", "-p", required=True, help="Garmin Connect account password")
    garmin_parser.add_argument("--cookie-jar", default=".garmin-cookies.txt", help="Filename with authentication cookies")

    subparsers = parser.add_subparsers(title="Commands")

    parser_feed = subparsers.add_parser("feed", parents=[garmin_parser], description="Feed activities from Garmin Connect")
    parser_feed.add_argument("--activity-table", help="BigQuery activity table")
    parser_feed.add_argument("--export-tasks-queue", help="Export tasks queue")
    parser_feed.set_defaults(func=command_feed)

    parser_export = subparsers.add_parser("export", parents=[garmin_parser], description="Export activity file from Garmin Connect to GCS")
    parser_export.add_argument("--activity-id", help="Activity identifier")
    parser_export.add_argument("--gcs-bucket", help="GCS bucket")
    parser_export.set_defaults(func=command_export)

    parser_load = subparsers.add_parser("load", description="Load activity from GCS into BigQuery")
    parser_load.add_argument("--gcs-bucket", help="GCS bucket")
    parser_load.add_argument("--gcs-object", help="GCS object")
    parser_load.add_argument("--session-table", help="BigQuery session table")
    parser_load.add_argument("--record-table", help="BigQuery record table")
    parser_load.set_defaults(func=command_load)

    args = parser.parse_args()

    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=logging_level)

    args.func(args)


if __name__ == "__main__":
    main()
