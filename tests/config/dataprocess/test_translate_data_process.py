import unittest
import re

from transpydata.config.dataprocess import TranslateDataProcess


class TestTranslateDataProcess(unittest.TestCase):

    def test_data_translate(self):
        config = {
            'translations': {
                'name': 'userName',
                'category': 'type'
            }
        }
        data = self._get_test_data()

        translate_process = TranslateDataProcess(config)
        translate_process.initialize()

        res = translate_process.process_one(data)

        name = data['name']
        del(data['name'])
        category = data['category']
        del(data['category'])

        self.assertDictEqual({
            'userName': name,
            'type': category,
            **data
        }, res)

    def test_data_transform(self):
        config = {
            'transformations': {
                'name': lambda n: re.sub('\-\d', '', n),
            }
        }
        data = self._get_test_data()

        translate_process = TranslateDataProcess(config)
        translate_process.initialize()

        res = translate_process.process_one(data)

        data['name'] = 'Cade'

        self.assertDictEqual(data, res)

    def test_data_exclude(self):
        config = {
            'exclude': ['category', 'weapon']
        }
        data = self._get_test_data()

        translate_process = TranslateDataProcess(config)
        translate_process.initialize()
        res = translate_process.process_one(data)

        del(data['category'])
        del(data['weapon'])

        self.assertDictEqual(data, res)

    def _get_test_data(self):
        return {
            'name': 'Cade-6',
            'category': 'character',
            'weapon': 'Ace of spades',
            'class': 'hunters'
        }
