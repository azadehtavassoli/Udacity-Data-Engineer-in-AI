from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadDimensionOperator(BaseOperator):

    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 postgres_conn_id='',
                 sql='',
                 table='',
                 truncate=True,
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        # Map params here
        self.postgres_conn_id = postgres_conn_id
        self.sql = sql
        self.table = table
        self.truncate = truncate

    def execute(self, context):
        self.log.info('LoadDimensionOperator not implemented yet')
        if self.truncate:
            self.log.info(f'Truncate table {self.table}')
            postgres.run(f'TRUNCATE {self.table}')

        self.log.info(f'Dimension table {self.table} is loaded.')
        postgres.run(f'INSERT INTO {self.table} {self.sql}')
