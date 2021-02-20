terraform {
  required_version = "~> 0.14"

  backend "remote" {
    organization = "mkuthan"

    workspaces {
      name = "garmin-gcp"
    }
  }

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

resource "google_storage_bucket" "garmin_gcp_bucket" {
  name     = "garmin-gcp-${random_string.id.result}"
  location = "EU"
}

output "bucket_id" {
  value = google_storage_bucket.garmin_gcp_bucket.id
}
