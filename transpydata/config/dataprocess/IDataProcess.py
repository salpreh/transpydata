from typing import List
from abc import ABCMeta, abstractmethod

from transpydata.config import IConfigurable, IProcessor, IResourceAware
from transpydata.util.decorators import duckyinterface


@duckyinterface
class IDataProcess(IProcessor, IConfigurable, IResourceAware, metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        pass #TODO: Add method checks

    def process_one_method_name(self) -> str:
        return 'process_one'

    def process_all_method_name(self) -> str:
        return 'process_all'

    @abstractmethod
    def process_one(self, data: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def process_all(self, data: List[dict]) -> List[dict]:
        raise NotImplementedError

    def initialize(self):
        pass

    def dispose(self):
        pass
