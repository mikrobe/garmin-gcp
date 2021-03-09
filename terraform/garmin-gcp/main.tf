terraform {
  backend "remote" {
    organization = "mkuthan"

    workspaces {
      name = "garmin-gcp"
    }
  }

  required_version = "~> 0.14"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.57.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.1.0"
    }
  }
}

provider "google" {
  project = var.gcp_project
  region  = var.gcp_region
}

resource "random_string" "id" {
  length  = 8
  special = false
  upper   = false
}

resource "google_app_engine_application" "app" {
  location_id = var.app_engine_location
}

resource "google_pubsub_topic" "scheduler_daily_topic" {
  name = "daily-jobs-${random_string.id.result}"
}

resource "google_cloud_scheduler_job" "scheduler_daily_job" {
  name     = "daily-job-${random_string.id.result}"
  schedule = "0 0 * * *"

  pubsub_target {
    topic_name = google_pubsub_topic.scheduler_daily_topic.id
    data       = base64encode(" ")
  }
}

resource "google_pubsub_topic" "scheduler_hourly_topic" {
  name = "hourly-jobs-${random_string.id.result}"
}

resource "google_cloud_scheduler_job" "scheduler_hourly_job" {
  name     = "hourly-job-${random_string.id.result}"
  schedule = "0 * * * *"

  pubsub_target {
    topic_name = google_pubsub_topic.scheduler_hourly_topic.id
    data       = base64encode(" ")
  }
}

resource "google_storage_bucket" "stage_bucket" {
  name     = "stage-${random_string.id.result}"
  location = var.bucket_location
}

resource "google_storage_bucket" "activity_bucket" {
  name     = "activity-${random_string.id.result}"
  location = var.bucket_location
}

resource "google_bigquery_dataset" "activity_dataset" {
  dataset_id = "activity"
  location   = var.dataset_location
}

module "activity_table" {
  source = "../modules/big-query-table"

  dataset_id = google_bigquery_dataset.activity_dataset.dataset_id
  table_id   = "activity"

  schema = file("${path.module}/schemas/activity.json")
}

module "session_table" {
  source = "../modules/big-query-table"

  dataset_id = google_bigquery_dataset.activity_dataset.dataset_id
  table_id   = "session"

  schema = file("${path.module}/schemas/session.json")

  clustering = [
    "activity_id"
  ]
}

module "record_table" {
  source = "../modules/big-query-table"

  dataset_id = google_bigquery_dataset.activity_dataset.dataset_id
  table_id   = "record"

  schema = file("${path.module}/schemas/record.json")

  clustering = [
    "activity_id"
  ]
}


