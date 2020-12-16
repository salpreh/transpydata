from typing import Tuple
import sys
import unittest
import unittest.mock as mock

from transpydata.config.datainput.MysqlDataInput import MysqlDataInput


class TestMysqlDataInput(unittest.TestCase):
    def test_validate_get_one_query_call(self):
        mysql_input = MysqlDataInput()
        config = self._get_input_config()

        mysql_input.configure(config)

        mysql_input.initialize()
        data = mysql_input.get_one({'id': 'CS101'})

        self.assertDictEqual({
            'module_Id': 'CS101',
            'module_name': 'Introduction to Computing',
            'credits': 10
        }, data)

    def test_validate_get_all_query_call(self):
        mysql_input = MysqlDataInput()
        config = self._get_input_config()

        mysql_input.configure(config)

        mysql_input.initialize()
        data = mysql_input.get_all()

        self.assertEqual(len(data), 3)

    def _get_input_config(self):
        return {
        'db_config': {
            'user': 'testuser',
            'password': 't3stPass',
            'host': '127.0.0.1',
            'port': '3306',
            'database': 'migration'
        },
        'get_one_query': 'SELECT * FROM module WHERE credits <= %(credits)s AND module_Id = %(id)s',
        'get_all_query': 'SELECT * FROM module WHERE credits <= %(credits)s',
        'all_query_params': {'credits': 10}
    }
