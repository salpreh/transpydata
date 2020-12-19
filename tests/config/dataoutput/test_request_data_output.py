from typing import Tuple
import sys
import json
import unittest
import unittest.mock as mock

from transpydata.config.dataoutput import IDataOutput


class TestRequestDataOutput(unittest.TestCase):

    def test_send_static_url(self):
        requests_mock = self._get_requests_module_mock()
        request_output = self._get_request_data_output_instance(requests_mock)

        config = {
            'url': 'http://testurl.net/post/data',
            'headers': {'x-app-id': 'TEST'}
        }
        request_output.configure(config)

        data = self._get_dummy_payload()
        res = request_output.send_one(data)

        requests_mock.request.assert_called_once()

        req_data = self._get_request_mock_call_data(requests_mock)

        self.assertEqual(config['url'], req_data['url'])
        self.assertEqual(config['headers'], req_data['headers'])

    def test_send_dynamic_url(self):
        request_mock = self._get_requests_module_mock()
        request_output = self._get_request_data_output_instance(request_mock)

        config = {
            'url': 'http://testurl.net/category/{category}/{class}',
            'query_params': ['name'],
            'req_verb': 'PUT'
        }
        request_output.configure(config)

        data = self._get_dummy_payload()
        request_output.send_one(data)

        request_mock.request.assert_called_once()

        req_data = self._get_request_mock_call_data(request_mock)
        self.assertEqual('http://testurl.net/category/character/hunters',
                         req_data['url'])
        self.assertEqual(data[config['query_params'][0]],
                         req_data['query_params'][config['query_params'][0]])

    def test_json_response_parse(self):
        request_mock = self._get_requests_module_mock()
        request_output = self._get_request_data_output_instance(request_mock)

        config = {
            'url': 'http://testurl.net/category',
            'query_params': ['name'],
            'req_verb': 'PUT',
            'json_response': True
        }
        request_output.configure(config)

        data = self._get_dummy_payload()

        out_res = request_output.send_one(data)

        request_mock.request.assert_called_once()
        request_mock.request.return_value.json.assert_called_once()

    def _get_requests_module_mock(self, code=200, content='Message') -> mock.Mock:
        requests_mock = mock.Mock()
        requests_mock.request.return_value.status_code = code
        requests_mock.request.return_value.content = content

        return requests_mock

    def _get_request_data_output_instance(self, requests_mock: mock.Mock) -> IDataOutput:
        if 'requests' in sys.modules:
            del(sys.modules['requests'])
        if 'transpydata.config.dataoutput.RequestDataOutput' in sys.modules:
            del(sys.modules['transpydata.config.dataoutput.RequestDataOutput'])

        sys.modules['requests'] = requests_mock
        from transpydata.config.dataoutput.RequestDataOutput import RequestDataOutput

        return RequestDataOutput()

    def _get_request_mock_call_data(self, requests_mock: mock.Mock):
        args, kwargs = requests_mock.request.call_args

        return {
            'req_verb': args[0],
            'url': args[1],
            'headers': kwargs['headers'],
            'query_params': kwargs['params'],
            'data': kwargs['data']
        }


    def _get_dummy_payload(self):
        return {
            'name': 'Cade-6',
            'category': 'character',
            'weapon': 'Ace of spades',
            'class': 'hunters'
        }
