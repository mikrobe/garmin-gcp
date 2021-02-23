output "stage_bucket" {
  value = google_storage_bucket.stage_bucket.name
}

output "scheduler_daily_topic" {
  value = google_pubsub_topic.scheduler_daily_topic.id
}

output "scheduler_hourly_topic" {
  value = google_pubsub_topic.scheduler_hourly_topic.id
}
