import logging

from google.cloud import bigquery


class BigQueryClient(object):
    _INSERT_ROWS_BATCH_SIZE = 10000

    _LOG = logging.getLogger(__name__)

    def __init__(self):
        self.client = bigquery.Client()

    def insert_rows(self, table, iterable, batch_size=_INSERT_ROWS_BATCH_SIZE):
        table_ref = self.client.get_table(table)

        batch = []
        for row in iterable:
            if len(batch) < batch_size:
                batch.append(row)
            else:
                self._insert_rows(table_ref, batch)
                batch.clear()
        if batch:
            self._insert_rows(table_ref, batch)

    def _insert_rows(self, table_ref, rows):
        self._LOG.info("Insert %d rows into %s", len(rows), table_ref.full_table_id)
        errors = self.client.insert_rows(table_ref,
                                         rows,
                                         skip_invalid_rows=True,
                                         ignore_unknown_values=False)
        if errors:
            for error in errors:
                self._LOG.error(str(error))
