import re
import json
from typing import List
from requests import request

from .IDataOutput import IDataOutput


class RequestDataOutput(IDataOutput):
    """ DataOutput that performs requests. Config dict format:
    {
        'url': str, # Will interpolate data variables in url when is called by
            migration using "{var_name}" synthax
        'query_params', # Name of variables that must be used as query params
            in request
        'req_verb': str, # Default 'POST'
        'headers': dict,
        'encode_json': bool # Encode data dictionary to JSON. Default `False`
        'json_response': bool # Parse JSON response to object. Default `False`
    }
    """

    URL_PARSE_RX = re.compile('{([^}]*)}') # type: re.Pattern

    def __init__(self, config: dict = None):
        self._config = config

        self._url = ''
        self._query_params = []
        self._req_verb = 'POST'
        self._headers = {}

        self._encode_json = False
        self._json_response = False
        self._url_vars = []

        if config: self.configure(config)

    def configure(self, config: dict):
        self._url = config.get('url')
        if not self._url:
            raise RuntimeError("'url' paramter needed in configuration")

        self._req_verb = config.get('req_verb', self._req_verb)
        self._query_params = config.get('query_params', self._query_params)
        self._headers = config.get('headers', self._headers)

        self._json_response = config.get('json_response', self._json_response)
        self._encode_json = config.get('encode_json', self._encode_json)

        self._process_url()

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
        payload = data.copy()
        url = self._generate_url(payload)
        q_params = self._get_query_params(payload)

        if self._encode_json:
            payload = json.dumps(payload)

        res = request(self._req_verb, url, headers=self._headers,
                      params=q_params, data=payload)

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

    def _generate_url(self, data: dict) -> str:
        """ Generate url interpolating variables.

        Args:
            data (dict): Data where the variables values are searched

        Returns:
            str: Url
        """
        if not self._url_vars: return self._url

        try:
            var_map = {var:data[var] for var in self._url_vars}

            url = self._url
            for var, val in var_map.items():
                url = re.sub(f'{{{var}}}', val, url)

                # For now we are not going to sendig values that are used in
                # url in payload
                del(data[var])

            return url
        except KeyError as ke:
            raise RuntimeError('Value for url variable not found', data) from ke

    def _get_query_params(self, data: dict) -> dict:
        q_params = {}
        for var in self._query_params:
            val = data.get(var)
            if val is None: continue

            q_params[var] = val

            # For now we are not going to sendig values that are used in
            # url in payload
            del(data[var])

        return q_params

    def _process_url(self):
        self._url_vars = self.URL_PARSE_RX.findall(self._url)
