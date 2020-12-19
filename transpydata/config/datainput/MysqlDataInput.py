import mysql.connector

from .IDataInput import IDataInput


class MysqlDataInput(IDataInput):
    """ DataInput to get data from Mysql. Config dict format:
    {
        'db_config': {
            'user': str,
            'password': str,
            'host': str,
            'port': int,
            'database': str
        },
        'get_one_query': str, # One item query. Interpolate variables with
            printf synthax. E.j: SELECT * FROM X WHERE id = %(id)s

        'get_all_query': str, # Query to get all items. Interpolate variables
            with printf synthax

        'all_query_params': dict, # Params to interpolate in query
    }

    """
    def __init__(self, config: dict = None):
        self._config = config

        self._db_config = None # type: dict
        self._db_connection = None # type: mysql.connection.MySQLConnection
        self._get_one_query = ''
        self._get_all_query = ''
        self._all_query_params = {}

        self._page_size = 0 # TODO: Not used for now

        if config: self.configure(config)

    def configure(self, config: dict):
        """Configure datainput. Refer to class doc to view the format

        Args:
            config (dict): configuration
        """
        self._config = config
        self._db_config = config['db_config']

        self._get_one_query = config.get('get_one_query', '')
        self._get_all_query = config.get('get_all_query', '')
        self._all_query_params = config.get('all_query_params', {})

        if not self._get_one_query and not self._get_all_query:
            raise RuntimeError(
                "'get_one_query' or 'get_all_query' needs to be provided"
            )

        self._page_size = config.get('page_size', None)

    def initialize(self):
        """ Create DB connection.
        """
        self._db_connection = mysql.connector.connect(**self._db_config)

    def dispose (self):
        """ Close DB connection.
        """
        if self._db_connection and self._db_connection.is_connected():
            self._db_connection.close()

    def _get_db_cursor(self) -> mysql.connector.cursor.MySQLCursor:
        return self._db_connection.cursor(dictionary=True)

    def get_all(self):
        return self._fetch_all_query(self._get_all_query, self._all_query_params)

    def get_one(self, data: dict):
        all_params = {**data, **self._all_query_params}
        return self._fetch_one_query(self._get_one_query, all_params)

    def _get_paged_query(self, query: str, num_page: int) -> str:

        # LIMIT
        offset = (num_page - 1) * self.page_size
        limit = f' LIMIT {offset}, {self.page_size}'

        return query + limit

    def _fetch_all_query(self, query: str, params: dict) -> dict:
        try:
            cursor = self._get_db_cursor()
            cursor.execute(query, params)

            return cursor.fetchall()

        finally:
            cursor.close()

        raise RuntimeError('Error performing query:\n'+query)

    def _fetch_one_query(self, query: str, params: dict) -> dict:
        try:
            cursor = self._get_db_cursor()
            cursor.execute(query, params)

            return cursor.fetchone()

        finally:
            cursor.close()

        raise RuntimeError('Error performing query:\n'+query)
