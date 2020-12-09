from typing import List
from abc import ABCMeta, abstractmethod

from transpydata.config import IConfigurable, IProcessor, IResourceAware
from transpydata.util.decorators import duckyinterface


@duckyinterface
class IDataOutput(IProcessor, IConfigurable, IResourceAware, metaclass=ABCMeta):

    def process_one_method_name(self) -> str:
        return 'send_one'

    def process_all_method_name(self) -> str:
        return 'send_all'

    @abstractmethod
    def send_one(self, data: dict) -> dict:
        """ Send one data entry to the implemented output destination.

        Args:
            data (dict): Data to send or configure the output
                (depends on implementation class)

        Returns:
            dict: Dict with details about send results.
        """
        raise NotImplementedError

    @abstractmethod
    def send_all(self, data: List[dict]) -> List[dict]:
        """ Send all data entries to the implemented output destination.

        Args:
            data (List[dict]): List of data to send or configure the output
                (depends on implementation class)

        Returns:
            List[dict]: List with details about send results.
        """
        raise NotImplementedError

    def initialize(self):
        pass

    def dispose(self):
        pass
