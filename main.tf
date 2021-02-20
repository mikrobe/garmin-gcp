terraform {
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

  backend "remote" {
    organization = "mkuthan"

    workspaces {
      name = "garmin-gcp"
    }
  }
}

provider "google" {
  project = "garmin-267619"
  region  = "europe-west1"
}

resource "random_id" "bucket_random_suffix" {
  byte_length = 8
}

resource "google_storage_bucket" "garmin_gcp_bucket" {
  name     = "garmin-gcp-${random_id.bucket_random_suffix}"
  location = "EU"
}

output "bucket_id" {
  value = google_storage_bucket.garmin_gcp_bucket.id
}
