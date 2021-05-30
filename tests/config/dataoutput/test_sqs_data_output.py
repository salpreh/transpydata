from typing import Tuple
import unittest
import os
import json
from uuid import uuid4

import boto3

from transpydata.config.dataoutput import SQSDataOutput

class TestSqsDataOutput(unittest.TestCase):

    BASE_URL = 'http://localstack:4566/'
    TEST_ACCOUNT = '000000000000'

    def test_send_one(self):
        sqs_queue_url = self._generate_sqs_url(os.environ['SQS_TEST_QUEUE'])
        self._purge_queue(sqs_queue_url)

        attributes, attributes_conf = self._get_attributes_config(
            self._get_test_attributes()
        )

        config = self._get_config(sqs_queue_url, attributes_conf)

        sqs_data_output = SQSDataOutput()
        sqs_data_output.configure(config)

        test_msg = self._get_test_msg()
        sqs_msg = {
            **test_msg,
            **self._get_test_attributes()
        }
        sqs_data_output.send_one(sqs_msg)

        sqs_msg_data = self._get_sqs_message(sqs_queue_url)

        self.assertDictEqual(test_msg, json.loads(sqs_msg_data['message']))

        attr_key = list(attributes.keys())[0]
        self.assertEqual(attributes[attr_key], sqs_msg_data['attributes'][attr_key]['StringValue'])


    def test_send_all(self):
        sqs_queue_url = self._generate_sqs_url(os.environ['SQS_TEST_QUEUE'])
        self._purge_queue(sqs_queue_url)

        attributes, attributes_conf = self._get_attributes_config(
            self._get_test_attributes()
        )

        config = self._get_config(sqs_queue_url, attributes_conf)

        sqs_data_output = SQSDataOutput()
        sqs_data_output.configure(config)

        test_msg1 = self._get_test_msg()
        test_msg2 = self._get_test_msg()
        sqs_msgs = [
            {
                **test_msg1,
                **self._get_test_attributes()
            },
            {
                **test_msg2,
                **self._get_test_attributes()
            }
        ]
        sqs_data_output.send_all(sqs_msgs)

        # Get and assert on first msg
        sqs_msg_data = self._get_sqs_message(sqs_queue_url)

        self.assertDictEqual(test_msg1, json.loads(sqs_msg_data['message']))

        attr_key = list(attributes.keys())[0]
        self.assertEqual(attributes[attr_key], sqs_msg_data['attributes'][attr_key]['StringValue'])

        # Get and assert on second msg
        sqs_msg_data = self._get_sqs_message(sqs_queue_url)

        self.assertDictEqual(test_msg2, json.loads(sqs_msg_data['message']))

    def _get_sqs_message(self, sqs_queue_url: str) -> dict:
        sqs_client = boto3.client('sqs', endpoint_url=self.BASE_URL)

        sqs_msg = sqs_client.receive_message(**self._receive_msg_config(sqs_queue_url))
        sqs_client.delete_message(
            QueueUrl = sqs_queue_url,
            ReceiptHandle = sqs_msg['Messages'][0]['ReceiptHandle']
        )

        return {
            'message': sqs_msg['Messages'][0]['Body'],
            'attributes': sqs_msg['Messages'][0]['MessageAttributes']
        }

    def _generate_sqs_url(self, sqs_queue):
        return f'{self.BASE_URL}{self.TEST_ACCOUNT}/{sqs_queue}'

    def _get_config(self, sqs_queue: str, attributes: dict) -> dict:
        return {
            'url': sqs_queue,
            'client_id': os.environ['AWS_ACCESS_KEY_ID'],
            'secret': os.environ['AWS_SECRET_ACCESS_KEY'],
            'region': os.environ['AWS_DEFAULT_REGION'],
            'endpoint_url': self.BASE_URL,
            'attributes': attributes
        }

    def _purge_queue(self, sqs_queue_url):
        boto3.client('sqs', endpoint_url = self.BASE_URL).purge_queue(QueueUrl=sqs_queue_url)

    def _receive_msg_config(self, sqs_queue_url) -> dict:
        return {
            'QueueUrl': sqs_queue_url,
            'MessageAttributeNames': ['All'],
            'MaxNumberOfMessages': 1
        }

    def _get_test_attributes(self) -> dict:
        return {
            'attr1': '12',
            'attr2': '23'
        }

    def _get_attributes_config(self, attributes: dict) -> Tuple[dict, dict]:
        new_attributes = {}
        attributes_conf = {}
        for i, (attr_name, attr_val) in enumerate(attributes.items()):
            new_name = f'tr_name_{i}'
            attributes_conf[attr_name] = new_name
            new_attributes[new_name] = attr_val

        return new_attributes, attributes_conf

    def _get_test_msg(self) -> dict:
        return {
            'id': str(uuid4()),
            'name': 'Nerevar',
            'house': 'Indoril',
            'race': 'Chimer'
        }
