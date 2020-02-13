def import_activities(event, context):
    print("""This Function was triggered by messageId {} published at {}""".format(context.event_id, context.timestamp))

    print(event)
