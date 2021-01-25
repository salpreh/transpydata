from typing import List, Dict, Any
from uuid import uuid4
import json

import boto3
from botocore.exceptions import ClientError

from . import IDataInput


class SQSDataInput(IDataInput):
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
        'parse_body_as_json': bool,
        'flatten_attributes': bool, # Put SQS attributes as first level message
            fields (only works if 'parse_body_as_json' is enabled).
            If not the result dict will contain one field 'message' and
            another 'attributes' with the data inside.
        'delete_messages': bool # Delete messages after processing. Defaults to `true`.
    }

    """

    MAX_BATCH_SIZE = 10 # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Client.receive_message
    MAX_RETRIES = 3

    BODY_KEY = 'message'
    ATTR_KEY = 'attributes'

    def __init__(self, config: dict = None):
        self.url = None
        self.flatten_attributes = False
        self.parse_body_as_json = False
        self.delete_messages = True

        self._client_id = ''
        self._secret = ''
        self._region = ''
        self._session_token = ''
        self._endpoint_url = ''
        self._sqs_client = None

        if config:
            self.configure(config)

    def configure(self, config: dict):
        self.url = config.get('url')
        if not self.url:
            raise RuntimeError("'url' parameter expected in configuration")

        self.flatten_attributes = config.get('flatten_attributes', self.flatten_attributes)
        self.parse_body_as_json = config.get('parse_body_as_json', self.parse_body_as_json)

        self._client_id = config.get('client_id', self._client_id)
        self._secret = config.get('secret', self._secret)
        self._region = config.get('region', self._region)
        self._session_token = config.get('session_token', self._session_token)
        self._endpoint_url = config.get('endpoint_url', self._endpoint_url)
        self.delete_messages = config.get('delete_messages', self.delete_messages)

    def get_one(self, data: dict = {}) -> dict:
        sqs_req = {
            'QueueUrl': self.url,
            'MessageAttributeNames': ['All'],
            'MaxNumberOfMessages': 1
        }
        sqs_client = self._get_sqs_client()

        res = sqs_client.receive_message(**sqs_req)

        result = self._process_response(res)
        if self.delete_messages:
            self._delete_messages(res)

        if len(result): return result[0]

        return {}

    def get_all(self) -> List[dict]:
        req_attempt_id = str(uuid4())
        res_messages = True
        retries = 0
        sqs_client = self._get_sqs_client()

        result = []
        while res_messages and retries < self.MAX_RETRIES:
            try:
                sqs_res = sqs_client.receive_message(
                    QueueUrl = self.url,
                    MessageAttributeNames = ['All'],
                    MaxNumberOfMessages = self.MAX_BATCH_SIZE,
                    ReceiveRequestAttemptId = req_attempt_id
                )
            except ClientError:
                retries += 1
                continue

            msgs = self._process_response(sqs_res)
            if self.delete_messages:
                self._delete_messages(sqs_res)

            result.extend(msgs)

            res_messages = len(msgs)
            retries = 0
            req_attempt_id = str(uuid4())

        if retries > self.MAX_RETRIES:
            self.logger.warn('Finished processing because max retries reached')

        return result

    def _process_response(self, sqs_res: dict) -> List[dict]:
        proc_res = []
        if not 'Messages' in sqs_res: return []

        for msg in sqs_res['Messages']:
            proc_res.append(self._process_msg(msg))

        return proc_res

    def _delete_messages(self, sqs_res: dict):
        sqs_client = self._get_sqs_client()
        if not 'Messages' in sqs_res: return

        for msg in sqs_res['Messages']:
            sqs_client.delete_message(
                QueueUrl = self.url,
                ReceiptHandle = msg['ReceiptHandle']
            )

    def _process_msg(self, msg: dict) -> dict:
        if not self.parse_body_as_json:
            return {
                self.BODY_KEY: msg['Body'],
                self.ATTR_KEY: self._process_attributes(msg['MessageAttributes'])
            }

        msg_body = json.loads(msg['Body'])
        msg_attr = self._process_attributes(msg['MessageAttributes'])

        proc_msg = {}
        if self.flatten_attributes:
            proc_msg = {**msg_body, **msg_attr}
        else:
            proc_msg = {
                self.BODY_KEY: msg_body,
                self.ATTR_KEY: msg_attr
            }

        return proc_msg

    def _process_attributes(self, attributes: Dict[str, dict]) -> Dict[str, Any]:
        proc_attr = {}
        for attr_name, attr_data in attributes.items():
            attr_val = None
            if attr_data['DataType'] in ['String', 'Number']:
                attr_val = attr_data['StringValue']
            else:
                attr_val = attr_data['BinaryValue']

            proc_attr[attr_name] = attr_val

        return proc_attr

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
