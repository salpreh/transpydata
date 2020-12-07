from typing import List
from abc import ABCMeta, abstractmethod

from .. import IConfigurable, IProcessor, IResourceAware


class IDataInput(IProcessor, IConfigurable, IResourceAware, metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        pass #TODO: Add method checks

    def process_one_method_name(self) -> str:
        return 'get_one'

    def process_all_method_name(self) -> str:
        return 'get_all'

    @abstractmethod
    def get_one(self, data: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> List[dict]:
        raise NotImplementedError

    def initialize(self):
        pass

    def dispose(self):
        pass

