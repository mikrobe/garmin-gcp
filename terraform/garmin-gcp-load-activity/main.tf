terraform {
  backend "remote" {
    organization = "mkuthan"

    workspaces {
      name = "garmin-gcp-load-activity"
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
  stage_bucket             = data.terraform_remote_state.main.outputs.stage_bucket
}


module "hello_world" {
  source = "../modules/cloud-functions"

  gcp_project = var.gcp_project
  gcp_region  = var.gcp_region

  entry_point         = "hello_world"
  event_trigger_type = "google.storage.object.finalize"
  event_trigger_resource = "todo"

  source_dir = "${path.root}/../../functions"
  stage_dir  = "${path.root}/../../build"

  stage_bucket = local.stage_bucket
}
