output "stage_bucket" {
  value = google_storage_bucket.stage_bucket.name
}

output "activities_bucket" {
  value = google_storage_bucket.activities_bucket.name
}

output "activities_dataset" {
  value = google_bigquery_dataset.activity_dataset.id
}

//output "activity_table" {
//  value = activity_table.table_id
//}
//
//output "record_table" {
//  value = record_table.table_id
//}terra

output "scheduler_daily_topic" {
  value = google_pubsub_topic.scheduler_daily_topic.id
}

output "scheduler_hourly_topic" {
  value = google_pubsub_topic.scheduler_hourly_topic.id
}
