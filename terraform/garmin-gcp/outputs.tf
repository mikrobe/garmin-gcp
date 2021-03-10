output "stage_bucket_name" {
  value = google_storage_bucket.stage_bucket.name
}

output "activity_bucket_name" {
  value = google_storage_bucket.activity_bucket.name
}

output "activity_dataset_id" {
  value = google_bigquery_dataset.activity_dataset.dataset_id
}

output "activity_table_id" {
  value = module.activity_table.table_id
}

output "session_table_id" {
  value = module.session_table.table_id
}

output "record_table_id" {
  value = module.record_table.table_id
}

output "scheduler_daily_topic_id" {
  value = google_pubsub_topic.scheduler_daily_topic.id
}

output "scheduler_hourly_topic_id" {
  value = google_pubsub_topic.scheduler_hourly_topic.id
}

output "export_tasks_queue_id" {
  value = google_cloud_tasks_queue.export_tasks_queue.id
}
