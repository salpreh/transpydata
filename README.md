# TransPyData

[![PyPI version](https://badge.fury.io/py/transpydata.svg)](https://badge.fury.io/py/transpydata)
[![PyPI version](https://img.shields.io/github/license/salpreh/transpydata.svg)](https://img.shields.io/github/license/salpreh/transpydata.svg)

**A minimal framework for managing migrations**

---

## Overview
TransPyData implements a generic pipeline to perform migrations. It has 2 main components. First one is `TransPy` class, which executes the migration pipeline according to a configuration. Second the _data services_ implementations (`IDataInput`, `IDataProcess` and `IDataOutput`), this services manages how data is gathered, processed and sent to the new destination.

### TransPy
The `TransPy` class manages the migration pipeline. It needs to be provided with an instance of: 
- `IDataInput`: Manages the gathering of source data.
- `IDataProcess`: Manages data transformation and filtering prior to pass it to the data output.
- `IDataOutput`: Manages data sending to the new destination.

_**NOTE**: Data services overview below_

Apart from the data services there are other optional configurations:
```python
trans_py = TransPy()

config = {
  'datainput_source': [], # If working with single record pipeline this should be an iterable of data to feed IDataInput
  'datainput_by_one': False, # Enable single record pipeline on input
  'dataprocess_by_one': False, # Enable single record pipeline on processing
  'dataoutput_by_one': False, # Enable single record pipeline on output
}
trans_py.configure(config)
```

The values in the snippet are the defaults, so by default the migration will move all migration data through the pipeline at once.

#### All processing mode
When all data services have the "_by\_one_" flag to `False` the migration will move all data at once through the pipeline. So the `TransPy` instance will call the method `get_all` of `IDataInput` configured to get all input data, with the response will call `process_all` of `IDataProcess`, and with the response of `IDataProcess` will call `send_all` of `IDataOutput`. Finally a list with `IDataOutput` results is returned by `TransPy`.

#### Single record mode
If "_by\_one_" flags are `True` the data are "_queried_" by one and moved through all the pipeline. The `IDataOutput` return are accumulated and returned as list at the end of the processing, so the `TransPy` return type is the same.

There are some additional cases, what if ***datainput*** and ***dataprocess*** are in "_by\_one_" mode and dataoutput not? In this case the data is gathered and processed one by one, at the end of processing (`IDataProcess`) the results are accumulated and the `IDataOutput` is called with all data. Similar case when ***dataprocess*** and ***dataoutput*** are in "_by\_one_" mode, data is gathered all at once and then piped one by one through `IDataProcess` and `IDataOutput`.

### Data services
_under construction_

## Getting started
To start a migration create an instance of `TransPy` and configure it. At least instances of `IDataInput`, `IDataProcess` and `IDataOutput` needs to be provided. Prior to starting the migration the data services might need to be configured too. Here is an code example:

```python
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
        'get_one_query': None, # We'll go with all query
        'get_all_query': """
            SELECT s.staff_Id, s.staff_name, s.staff_grade, m.module_Id, m.module_name
            FROM staff s
            LEFT JOIN teaches t ON s.staff_Id = t.staff_Id
            LEFT JOIN module m ON t.module_Id = m.module_Id
        """,
        'all_query_params': {} # No where clause, no interpolation
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
```

Full working example could be found at `examples/mysql_to_http/`, there is a [docker-compose](https://docs.docker.com/compose/gettingstarted/#step-6-re-build-and-run-the-app-with-compose) to launch an instance of mysql and a webserver.

## Custom data services
For now you can check the interfaces `IDataInput`, `IDataProcess` and `IDataOutput` to see what needs to be implemented in a custom data service.

_(I'll improve this section in the future)_

