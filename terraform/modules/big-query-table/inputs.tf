variable "dataset_id" {
  type = string
}

variable "table_id" {
  type = string
}

variable "schema" {
  type = string
}

variable "time_partitioning" {
  type    = object({
    field                    = string,
    type                     = string,
    require_partition_filter = bool
  })
  default = {
    field                    = "timestamp"
    type                     = "DAY"
    require_partition_filter = true
  }
}

variable "clustering" {
  type    = list(string)
  default = []
}