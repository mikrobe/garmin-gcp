# garmin-gcp

## Cloud Scheduler

Create an App Engine app within the current Google Cloud Project:

```shell script
$ gcloud app create --region=europe-west
Creating App Engine application in project [foo-123] and region [europe-west]....done.
Success! The app is now created. Please use `gcloud app deploy` to deploy your first app.
```

Check the region of an existing app with the command:

```shell script
$ gcloud app describe
authDomain: gmail.com
codeBucket: staging.foo-123.appspot.com
databaseType: CLOUD_DATASTORE_COMPATIBILITY
defaultBucket: foo-123.appspot.com
defaultHostname: foo-123.appspot.com
featureSettings:
  splitHealthChecks: true
  useContainerOptimizedOs: true
gcrDomain: eu.gcr.io
id: foo-123
locationId: europe-west
name: apps/foo-123
servingStatus: SERVING
```

Create PubSub topic for scheduled events:

```shell script
$ gcloud pubsub topics create minute-jobs
Created topic [projects/foo-123/topics/minute-jobs].
```

Schedule events published to PubSub topic every minute:
```shell script
$ gcloud scheduler jobs create pubsub minute-job \
  --schedule "* * * * *" --topic minute-jobs --message-body " "
name: projects/foo-123/locations/europe-west1/jobs/minute-job
pubsubTarget:
  data: IA==
  topicName: projects/foo-123/topics/minute-jobs
retryConfig:
  maxBackoffDuration: 3600s
  maxDoublings: 16
  maxRetryDuration: 0s
  minBackoffDuration: 5s
schedule: '* * * * *'
state: ENABLED
timeZone: Etc/UTC
userUpdateTime: '2020-02-13T16:03:25Z'
```

Cron job could be paused and resumed:
```shell script
$ gcloud scheduler jobs pause minute-job
Job has been paused.
```

```shell script
$ gcloud scheduler jobs resume minute-job
Job has been resumed.
```

## Cloud Functions

Create stage bucket for Cloud functions:

```shell script
$ gsutil mb -c regional -l europe-west1 gs://garmin-gcp-functions-bucket
Creating gs://garmin-gcp-functions-bucket/...
```


Deploy Cloud function for importing activities:

```shell script
gcloud functions deploy import_activities \
  --region=europe-west1 --allow-unauthenticated \
  --stage-bucket=garmin-gcp-functions-bucket \
  --source=./functions/import_activities --runtime=python37 \
  --trigger-topic minute-jobs
Deploying function (may take a while - up to 2 minutes)...done.
availableMemoryMb: 256
entryPoint: import_activities
eventTrigger:
  eventType: google.pubsub.topic.publish
  failurePolicy: {}
  resource: projects/foo-123/topics/minute-jobs
  service: pubsub.googleapis.com
ingressSettings: ALLOW_ALL
labels:
  deployment-tool: cli-gcloud
name: projects/foo-123/locations/us-central1/functions/import_activities
runtime: python37
serviceAccountEmail: foo-123@appspot.gserviceaccount.com
sourceUploadUrl: gs://garmin-gcp-functions-bucket/us-central1-projects/foo-123/locations/europe-west1/functions/import_activities-sfxhgkmejddc.zip
status: ACTIVE
timeout: 60s
updateTime: '2020-02-13T16:25:21Z'
versionId: '1'
```