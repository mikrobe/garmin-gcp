import logging

from google.cloud import bigquery


class BigQueryClient(object):
    _INSERT_ROWS_CHUNK_SIZE = 10000

    _LOG = logging.getLogger(__name__)

    def __init__(self):
        self.client = bigquery.Client()

    def insert_rows(self, table_id, dataset):
        table = self.client.get_table(table_id)
        for i in range(0, len(dataset), BigQueryClient._INSERT_ROWS_CHUNK_SIZE):
            self._insert_rows(table, dataset[i:i + BigQueryClient._INSERT_ROWS_CHUNK_SIZE])

    def _insert_rows(self, table, dataset_chunked):
        self._LOG.info("Insert %d rows into %s", len(dataset_chunked), table.full_table_id)
        errors = self.client.insert_rows(table,
                                         dataset_chunked,
                                         skip_invalid_rows=True,
                                         ignore_unknown_values=False)
        if errors:
            for error in errors:
                self._LOG.error(str(error))
