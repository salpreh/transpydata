import json
from typing import List
from requests import request

from .IDataOutput import IDataOutput


class RequestDataOutput(IDataOutput):
    """ DataOutput that performs requests. Config dict format:
    {
        'url': str,
        'req_verb': str, # Default 'POST'
        'headers': dict,
        'encode_json': bool # Encode data dictionary to JSON. Default `False`
        'json_response': bool # Parse JSON response to object. Default `False`
    }
    """

    def __init__(self, config: dict = None):
        self._config = config

        self._url = ''
        self._req_verb = 'POST'
        self._headers = {}

        self._encode_json = False
        self._json_response = False

        if config: self.configure(config)

    def configure(self, config: dict):
        self._url = config.get('url')
        if not self._url:
            raise RuntimeError("'url' paramter needed in configuration")

        self._req_verb = config.get('req_verb', self._req_verb)
        self._headers = config.get('headers', self._headers)

        self._json_response = config.get('json_response', self._json_response)
        self._encode_json = config.get('encode_json', self._encode_json)

    def send_one(self, data: dict) -> dict:
        """ Sends requests and return a dict with fields:
         - `code`: Response code
         - `message`: Content of the response (dict if parse JSON is activated,
           bytes otherwise)

        Args:
            data (dict): Payload data.

        Returns:
            dict: Response data (code and message).
        """
        payload = data
        if self._encode_json:
            payload = json.dumps(data)

        res = request(self._req_verb, self._url, headers=self._headers,
                data=payload)

        msg = res.content
        if self._json_response:
            msg = res.json()

        return {'code': res.status_code, 'message': msg}

    def send_all(self, data: List[dict]) -> List[dict]:
        """ Sends are request per dict mesasge in list. Returns a list of
        responses as specified in `self.send_one`.

        Args:
            data (List[dict]): List of payloads for requests.

        Returns:
            List[dict]: Responses data (code and message per request).
        """
        return [self.send_one(d) for d in data]

