import unittest
import os
import json

import boto3

from transpydata.config.datainput import SQSDataInput

class TestSqsDataInput(unittest.TestCase):

    BASE_URL = 'http://localstack:4566/'
    TEST_ACCOUNT = '000000000000'

    def test_get_one(self):
        sqs_queue_url = self._generate_sqs_url(os.environ['SQS_TEST_QUEUE'])
        self._purge_queue(sqs_queue_url)

        attributes = self._get_test_attributes()
        msg = self._get_test_msg()

        config = self._get_config(sqs_queue_url, attributes.keys())

        sqs_datainput = SQSDataInput()
        sqs_datainput.configure(config)

        self._post_msg_to_sqs(sqs_queue_url, msg, attributes)
        sqs_msg = sqs_datainput.get_one()

        self.assertDictEqual(msg, sqs_msg[SQSDataInput.BODY_KEY])
        self.assertDictEqual(attributes, sqs_msg[SQSDataInput.ATTR_KEY])

        # TODO: Test message removal
        sqs_msg = sqs_datainput.get_one()
        self.assertFalse(sqs_msg)

    def test_get_all(self):
        sqs_queue_url = self._generate_sqs_url(os.environ['SQS_TEST_QUEUE'])
        self._purge_queue(sqs_queue_url)

        attributes = self._get_test_attributes()
        msg1 = self._get_test_msg()
        msg2 = self._get_test_msg()

        config = self._get_config(sqs_queue_url, attributes.keys())

        sqs_datainput = SQSDataInput()
        sqs_datainput.configure(config)

        self._post_msg_to_sqs(sqs_queue_url, msg1, attributes)
        self._post_msg_to_sqs(sqs_queue_url, msg2, attributes)

        sqs_msgs = sqs_datainput.get_all()

        self.assertEqual(2, len(sqs_msgs))
        self.assertDictEqual(msg1, sqs_msgs[1][SQSDataInput.BODY_KEY])

    def _post_msg_to_sqs(self, sqs_queue: str, msg: dict, attributes: dict = {}):
        sqs_client = boto3.client('sqs', endpoint_url = self.BASE_URL)

        sqs_client.send_message(
            QueueUrl = sqs_queue,
            MessageBody = json.dumps(msg),
            MessageAttributes = self._process_attributes(attributes)
        )

    def _process_attributes(self, attributes: dict):
        proc_attributes = {}
        for attr_name, attr_val in attributes.items():
            proc_attributes[attr_name] = {
                'DataType': 'String',
                'StringValue': str(attr_val)
            }

        return proc_attributes

    def _purge_queue(self, sqs_queue_url):
        boto3.client('sqs', endpoint_url = self.BASE_URL).purge_queue(QueueUrl=sqs_queue_url)

    def _generate_sqs_url(self, sqs_queue):
        return f'{self.BASE_URL}{self.TEST_ACCOUNT}/{sqs_queue}'

    def _get_config(self, sqs_queue: str, attributes: list) -> dict:
        return {
            'url': sqs_queue,
            'client_id': os.environ['AWS_ACCESS_KEY_ID'],
            'secret': os.environ['AWS_SECRET_ACCESS_KEY'],
            'region': os.environ['AWS_DEFAULT_REGION'],
            'endpoint_url': self.BASE_URL,
            'attributes': attributes,
            'parse_body_as_json': True,
            'flatten_attributes': False
        }

    def _get_test_attributes(self) -> dict:
        return {
            'attr1': '12',
            'attr2': '23'
        }

    def _get_test_msg(self) -> dict:
        return {
            'name': 'Nerevar',
            'house': 'Indoril',
            'race': 'Chimer'
        }
