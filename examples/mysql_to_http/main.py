import json

from transpydata import TransPy
from transpydata.config.datainput.MysqlDataInput import MysqlDataInput
from transpydata.config.dataprocess.NoneDataProcess import NoneDataProcess
from transpydata.config.dataoutput.RequestDataOutput import RequestDataOutput


def main():
    # Configure imput
    mysql_input = MysqlDataInput()

    config = {
        'db_config': {
            'user': 'root',
            'password': 'TryingTh1ngs',
            'host': 'localhost',
            'port': '3306',
            'database': 'migration'
        },
        'get_one_query': None, # We'll go with batch
        'get_all_query': """
            SELECT s.staff_Id, s.staff_name, s.staff_grade, m.module_Id, m.module_name
            FROM staff s
            LEFT JOIN teaches t ON s.staff_Id = t.staff_Id
            LEFT JOIN module m ON t.module_Id = m.module_Id
        """,
        'all_query_params': {}
    }
    mysql_input.configure(config)

    # Configure process
    none_process = NoneDataProcess()

    # Configure output
    request_output = RequestDataOutput()
    request_output.configure({
        'url': 'http://localhost:8008',
        'req_verb': 'POST',
        'headers': {
            'content-type': 'application/json',
            'accept-encoding': 'application/json',
            'x-app-id': 'MT1'
        },
        'encode_json': True,
        'json_response': True
    })

    # Configure TransPy
    trans_py = TransPy()
    trans_py.datainput = mysql_input
    trans_py.dataprocess = none_process
    trans_py.dataoutput = request_output

    res = trans_py.run()
    print(json.dumps(res))

if __name__ == '__main__':
    main()
