terraform {
  backend "remote" {
    organization = "mkuthan"

    workspaces {
      name = "garmin-gcp-import-wellness"
    }
  }

  required_version = "~> 0.14"

  required_providers {
    google  = {
      source  = "hashicorp/google"
      version = "3.57.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "2.1.0"
    }
  }
}

data "terraform_remote_state" "main" {
  backend = "remote"

  config = {
    organization = "mkuthan"

    workspaces = {
      name = "garmin-gcp"
    }
  }
}

locals {
  import_wellness_function = "${path.root}/../../build/import_wellness.zip"
  random_string            = data.terraform_remote_state.main.outputs.random_string
  stage_bucket             = data.terraform_remote_state.main.outputs.stage_bucket
  scheduler_daily_topic    = data.terraform_remote_state.main.outputs.scheduler_daily_topic
}


data "archive_file" "import_wellness" {
  type        = "zip"
  output_path = local.import_wellness_function

  source {
    content  = file("${path.module}/../../requirements.txt")
    filename = "requirements.txt"
  }

  source {
    content  = file("${path.root}/../../functions/import_wellness.py")
    filename = "main.py"
  }

  source_dir = "${path.root}/../../functions/garmin"
  source_dir = "${path.root}/../../functions/models"
}

resource "google_storage_bucket_object" "hello_world" {
  name   = "hello_world.zip"
  bucket = local.stage_bucket
  source = local.hello_world_function
}

resource "google_cloudfunctions_function" "hello_world_function" {
  project = var.gcp_project
  region  = var.gcp_region

  name        = "hello-world-${local.random_string}"
  entry_point = local.hello_world_entry_point
  runtime     = "python39"

  source_archive_bucket = local.stage_bucket
  source_archive_object = google_storage_bucket_object.hello_world.name

  available_memory_mb = 128
  timeout             = 60

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = local.scheduler_daily_topic
  }
}