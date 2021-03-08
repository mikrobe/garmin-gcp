terraform {
  required_version = "~> 0.14"

  required_providers {
    google  = {
      source  = "hashicorp/google"
      version = ">= 3.57.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.1.0"
    }
  }
}

locals {
  archive_file = "${var.stage_dir}/${var.function_name}.zip"
}

resource "random_string" "id" {
  length  = 8
  special = false
  upper   = false
}

data "archive_file" "archive" {
  source_dir  = var.source_dir
  output_path = local.archive_file
  type        = "zip"
}

resource "google_storage_bucket_object" "archive_object" {
  source = local.archive_file
  bucket = var.stage_bucket
  name   = "${var.function_name}-${data.archive_file.archive.output_md5}.zip"
}

resource "google_cloudfunctions_function" "function" {
  project = var.gcp_project
  region  = var.gcp_region

  name        = var.function_name
  entry_point = var.entry_point

  environment_variables = var.environment_variables

  source_archive_bucket = var.stage_bucket
  source_archive_object = google_storage_bucket_object.archive_object.name

  runtime             = var.runtime
  available_memory_mb = var.available_memory_mb
  timeout             = var.timeout_sec

  event_trigger {
    event_type = var.event_trigger.type
    resource   = var.event_trigger.resource
  }
}
