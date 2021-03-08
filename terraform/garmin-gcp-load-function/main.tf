terraform {
  backend "remote" {
    organization = "mkuthan"

    workspaces {
      name = "garmin-gcp-load-function"
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
  stage_bucket_name    = data.terraform_remote_state.main.outputs.stage_bucket_name
  activity_bucket_name = data.terraform_remote_state.main.outputs.activity_bucket_name
  activity_dataset_id  = data.terraform_remote_state.main.outputs.activity_dataset_id
  session_table_id     = data.terraform_remote_state.main.outputs.session_table_id
  record_table_id      = data.terraform_remote_state.main.outputs.record_table_id
}

module "load_function" {
  source = "../modules/cloud-functions"

  gcp_project = var.gcp_project
  gcp_region  = var.gcp_region

  function_name = "load"
  entry_point   = "function_load"

  source_dir = "${path.root}/../../functions"
  stage_dir  = "${path.root}/../../build"

  stage_bucket = local.stage_bucket_name

  available_memory_mb = 256
  timeout_sec = 120

  environment_variables = {
    "SESSION_TABLE": "${local.activity_dataset_id}.${local.session_table_id}"
    "RECORD_TABLE": "${local.activity_dataset_id}.${local.record_table_id}"
  }

  event_trigger = {
    type     = "google.storage.object.finalize"
    resource = local.activity_bucket_name
  }
}
