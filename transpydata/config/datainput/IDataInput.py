from typing import List
from abc import ABCMeta, abstractmethod

from transpydata.config import IConfigurable, IProcessor, IResourceAware
from transpydata.util.decorators import duckyinterface


@duckyinterface
class IDataInput(IProcessor, IConfigurable, IResourceAware, metaclass=ABCMeta):

    def process_one_method_name(self) -> str:
        return 'get_one'

    def process_all_method_name(self) -> str:
        return 'get_all'

    @abstractmethod
    def get_one(self, data: dict) -> dict:
        """ Get one data input entry. User can pass data to parametrize the item
            he wants each time.

        Args:
            data (dict): Data to parametrize/query the data input.

        Returns:
            dict: Data entry
        """
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> List[dict]:
        """ Get all input data at once. The arguments needed to perform this
            action should be passed through configuration.

        Returns:
            List[dict]: List of data entries.
        """
        raise NotImplementedError

    def initialize(self):
        pass

    def dispose(self):
        pass

