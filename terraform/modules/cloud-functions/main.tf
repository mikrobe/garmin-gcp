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
    random  = {
      source  = "hashicorp/random"
      version = ">=3.1.0"
    }
  }
}

locals {
  function_name = "${var.entry_point}-${random_string.id.result}"
  archive_file  = "${var.stage_dir}/${local.function_name}.zip"
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
  name   = "${local.function_name}.zip"
}

resource "google_cloudfunctions_function" "function" {
  project = var.gcp_project
  region  = var.gcp_region

  name        = local.function_name
  entry_point = var.entry_point
  runtime     = var.runtime

  source_archive_bucket = var.stage_bucket
  source_archive_object = google_storage_bucket_object.archive_object.name

  available_memory_mb = 128
  timeout             = 60

  event_trigger {
    event_type = var.event_trigger_type
    resource   = var.event_trigger_resource
  }
}
