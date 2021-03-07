variable "gcp_project" {
  type = string
}

variable "gcp_region" {
  type = string
}

variable "entry_point" {
  type = string
}

variable "event_trigger_type" {
  type = string
}

variable "event_trigger_resource" {
  type = string
}

variable "runtime" {
  type    = string
  default = "python39"
}

variable "source_dir" {
  type = string
}

variable "stage_dir" {
  type = string
}

variable "stage_bucket" {
  type = string
}