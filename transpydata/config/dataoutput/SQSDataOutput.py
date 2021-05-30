from typing import Tuple, List
import json

import boto3
from botocore.exceptions import ClientError

from . import IDataOutput


class SQSDataOutput(IDataOutput):
    """ DataOutput that sends messages to AWS SQS.

    Config dict format:
    {
        'url': str, # SQS url
        'client_id': str, # AWS client id (optional, could be providad as env
            variable or default config file
            https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#using-environment-variables)
        'secret': str, # AWS client secret (optional, could be providad as env
            variable or default config file
            https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#using-environment-variables)
        'region': str, # AWS region (optional, could be providad as env
            variable or default config file
            https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#using-environment-variables)
        'session_token': str, # AWS session token (optional, could be providad as env
            variable or default config file
            https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#using-environment-variables)
        'endpoint_url': str, # AWS endpoint url config param. Mostly for local and development setups
        'attributes': dict, # Fields in data input that shoul go as attributes
            (key) and the name of the property (value)
    }

    """

    MAX_BATCH_SIZE = 10 # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Client.send_message_batch

    def __init__(self, config: dict = None):
        self.url = None
        self.attributes = {}

        self._client_id = ''
        self._secret = ''
        self._region = ''
        self._endpoint_url = ''
        self._session_token = ''
        self._sqs_client = None

        if config:
            self.configure(config)

    def configure(self, config: dict):
        self.url = config.get('url')
        if not self.url:
            raise RuntimeError("'url' parameter expected in configuration")

        self.attributes = config.get('attributes', self.attributes)
        self._client_id = config.get('client_id', self._client_id)
        self._secret = config.get('secret', self._secret)
        self._region = config.get('region', self._region)
        self._session_token = config.get('session_token', self._session_token)
        self._endpoint_url = config.get('endpoint_url', self._endpoint_url)

    def send_one(self, data: dict) -> dict:
        """ Send one data entry to SQS.

        Args:
            data (dict): SQS message data

        Returns:
            dict: Dict with process result. Result format:
            {
                'success': bool, # Whether messager has been posted correctly on SQS or not
                'message_id': str, # Message id in SQS (only if sucessful sending)
                'error': str, # Error in case of not successful sending
            }
        """
        sqs_client = self._get_sqs_client()
        sqs_msg = self._get_sqs_message_data(data)

        res = {}
        try:
            sqs_res = sqs_client.send_message(**sqs_msg)
            res = {'success': True, 'message_id': sqs_res['MessageId']}
        except ClientError as e:
            res = {'success': False, 'error': e}

        return res

    def send_all(self, data: List[dict]) -> List[dict]:
        """ Send a list of data entries to SQS.

        Args:
            data (List[dict]): SQS messages data

        Returns:
            List[dict]: List of dict entries with process result. Result format:
            {
                'success': bool, # Whether messager has been posted correctly on SQS or not
                'id': int, # Index of the message in the input data list
                'message_id': str, # Message id in SQS (only if sucessful sending)
                'error': str, # Error in case of not successful sending
            }
        """
        sqs_client = self._get_sqs_client()
        results = []
        for n in range(0, len(data), self.MAX_BATCH_SIZE):
            data_batch = data[n:n + self.MAX_BATCH_SIZE]
            sqs_data = self._get_sqs_messages_data(data_batch, n)

            sqs_res = sqs_client.send_message_batch(**sqs_data)
            results.extend(self._process_sqs_batch_result(sqs_res))

        return results

    def _process_sqs_batch_result(self, result: dict) -> List[dict]:
        proc_result = []
        if 'Successful' in result:
            for success_msg in result['Successful']:
                proc_result.append({
                    'success': True,
                    'id': success_msg['Id'],
                    'message_id': success_msg['MessageId']
                })

        if 'Failed' in result:
            for error_msg in result['Failed']:
                proc_result.append({
                    'success': False,
                    'id': error_msg['Id'],
                    'error': '[{}] {}'.format(error_msg['Code'], error_msg['Message'])
                })

        return proc_result

    def _get_sqs_messages_data(self, data: List[dict], start_id: int = 0) -> List[dict]:
        sqs_data = {'QueueUrl': self.url, 'Entries': []}
        for i, data_entry in enumerate(data, start=start_id):
            msg_data, attributes = self._process_data_and_attributes(data_entry)
            sqs_data['Entries'].append({
                'Id': str(i),
                'MessageBody': json.dumps(msg_data),
                'MessageAttributes': attributes
            })

        return sqs_data

    def _get_sqs_message_data(self, data: dict) -> dict:
        sqs_data = {'QueueUrl': self.url}

        msg_data, attributes = self._process_data_and_attributes(data)
        sqs_data['MessageBody'] = json.dumps(msg_data)
        sqs_data['MessageAttributes'] = attributes

        return sqs_data

    def _process_data_and_attributes(self, data: dict) -> Tuple[dict, dict]:
        """ Process data and split between message and attributes fields

        Args:
            data (dict): data

        Returns:
            Tuple[dict, dict]: First dict is messag data, second attributes data
        """
        if not self.attributes:
            return data, {}

        msg_data = {}
        msg_attributes = {}
        for key, val in data.items():
            if key in self.attributes.keys():
                msg_attributes[self.attributes[key]] = {
                    'StringValue': str(val),
                    'DataType': 'Number' if type(val) in [int, float] else 'String'
                }
            else:
                msg_data[key] = val

        return msg_data, msg_attributes

    def _get_sqs_client(self):
        if self._sqs_client:
            return self._sqs_client

        config = {}
        if self._client_id and self._secret:
            config['aws_access_key_id'] = self._client_id
            config['aws_secret_access_key'] = self._secret

        if self._region:
            config['region_name'] = self._region

        if self._session_token:
            config['aws_session_token'] = self._session_token

        if self._endpoint_url:
            config['endpoint_url'] = self._endpoint_url

        self._sqs_client = boto3.client('sqs', **config)

        return self._sqs_client
