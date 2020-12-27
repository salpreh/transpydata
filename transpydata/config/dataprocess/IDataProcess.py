from typing import List
from abc import ABCMeta, abstractmethod

from transpydata.config import IDataService
from transpydata.util.decorators import duckyinterface


@duckyinterface
class IDataProcess(IDataService, metaclass=ABCMeta):


    def __init__(self):
        super().__init__()

    def process_one_method_name(self) -> str:
        return 'process_one'

    def process_all_method_name(self) -> str:
        return 'process_all'

    @abstractmethod
    def process_one(self, data: dict) -> dict:
        """ Process one data entry.

        Args:
            data (dict): Data to process.

        Returns:
            dict: Processed data.
        """
        raise NotImplementedError

    @abstractmethod
    def process_all(self, data: List[dict]) -> List[dict]:
        """ Process all data entries.

        Args:
            data (List[dict]): List of data to be processed.

        Returns:
            List[dict]: List with data processed.
        """
        raise NotImplementedError

    def initialize(self):
        super().initialize()

    def dispose(self):
        pass
