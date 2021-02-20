locals {
  hello_world_function = "${path.root}/../build/hello_world.zip"
}

terraform {
  required_version = "~> 0.14"

  required_providers {
    google  = {
      source  = "hashicorp/google"
      version = "3.57.0"
    }
    random  = {
      source  = "hashicorp/random"
      version = "3.1.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "2.1.0"
    }
  }

  backend "remote" {
    organization = "mkuthan"

    workspaces {
      name = "garmin-gcp"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

resource "random_string" "id" {
  length  = 8
  special = false
  upper   = false
}

data "archive_file" "hello_world" {
  type        = "zip"
  output_path = local.hello_world_function

  source {
    content  = file("${path.root}/../functions/hello_world.py")
    filename = "main.py"
  }

  source {
    content  = file("${path.module}/../requirements.txt")
    filename = "requirements.txt"
  }
}

resource "google_app_engine_application" "app" {
  location_id = var.app_engine_location
}

resource "google_pubsub_topic" "scheduler_topic" {
  name = "minute-jobs-${random_string.id.result}"
}

resource "google_cloud_scheduler_job" "scheduler_job" {
  name     = "minute-job-${random_string.id.result}"
  schedule = "* * * * *"

  pubsub_target {
    topic_name = google_pubsub_topic.scheduler_topic.id
    data       = base64encode(" ")
  }
}

resource "google_storage_bucket" "stage_bucket" {
  name     = "stage-${random_string.id.result}"
  location = var.bucket_location
}

resource "google_storage_bucket_object" "hello_world" {
  name   = "hello_world.zip"
  bucket = google_storage_bucket.stage_bucket.name
  source = local.hello_world_function
}

resource "google_cloudfunctions_function" "hello_world_function" {
  name    = "hello-world-${random_string.id.result}"
  entry_point = "hello_pubsub"
  runtime = "python39"

  source_archive_bucket = google_storage_bucket.stage_bucket.name
  source_archive_object = google_storage_bucket_object.hello_world.name

  available_memory_mb = 128
  timeout             = 60

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.scheduler_topic.id
  }
}
