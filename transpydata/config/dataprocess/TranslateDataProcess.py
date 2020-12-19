from typing import List, Any, Tuple

from .IDataProcess import IDataProcess


class TranslateDataProcess(IDataProcess):
    """ DataProcess to change data fields names and preform tranformations on the
        values. Config dict foramat:
        {
            'exclude': list, # List of input fields to exclude
            'translations': dict, # Dict where keys are field names on
                input (generated data of DataInput) and values are a new name
                for that field
            'transformations': dict # Dict where keys are field names and
                values can be a function to execute on the value or a constat
                value to be asigned to that field
        }
    """


    def __init__(self, config: dict=None):
        self._config = config

        self._exclude = []
        self._translations = {}
        self._transformations = {}

        if config: self.configure(config)

    def configure(self, config: dict):
        self._exclude = config.get('exclude', self._exclude)
        self._translations = config.get('translations', self._translations)
        self._transformations = config.get('transformations',
                                           self._transformations)

    def process_one(self, data: dict) -> dict:
        """ Process one data entry.

        Args:
            data (dict): Data to process.

        Returns:
            dict: Processed data.
        """
        p_data = {}
        for k, v in data.items():
            if k in self._exclude: continue
            p_key, p_val = self._process_field(k, v)
            p_data[p_key] = p_val

        return p_data

    def process_all(self, data: List[dict]) -> List[dict]:
        """ Process all data entries.

        Args:
            data (List[dict]): List of data to be processed.

        Returns:
            List[dict]: List with data processed.
        """
        return [self.process_one(d) for d in data]


    def _process_field(self, key, value) -> Tuple[Any, Any]:
        r_key = self._translations.get(key, key)

        if not key in self._transformations:
            return r_key, value

        r_value = self._transformations.get(key)
        if callable(r_value):
            r_value = r_value(value)

        return r_key, r_value
