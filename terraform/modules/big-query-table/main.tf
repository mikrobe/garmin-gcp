resource "google_bigquery_table" "table" {
  dataset_id = var.dataset_id
  table_id   = var.table_id

  schema = var.schema

  time_partitioning {
    field                    = var.time_partitioning.field
    type                     = var.time_partitioning.type
    require_partition_filter = var.time_partitioning.require_partition_filter
  }

  clustering = var.clustering
}