variable "gcp_project" {
  type = string
}

variable "gcp_region" {
  type = string
}

variable "function_name" {
  type = string
}

variable "entry_point" {
  type = string
}

variable "environment_variables" {
  type = map
}

variable "runtime" {
  type    = string
  default = "python39"
}

variable "available_memory_mb" {
  type    = number
  default = 128
}

variable "timeout_sec" {
  type    = number
  default = 60
}

variable "event_trigger" {
  type = object({
    type     = string,
    resource = string
  })
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