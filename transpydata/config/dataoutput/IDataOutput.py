from typing import List
from abc import ABCMeta, abstractmethod

from .. import IConfigurable, IProcessor, IResourceAware


class IDataOutput(IProcessor, IConfigurable, IResourceAware, metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        pass #TODO: Add method checks

    def process_one_method_name(self) -> str:
        return 'send_one'

    def process_all_method_name(self) -> str:
        return 'send_all'

    @abstractmethod
    def send_one(self, data: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def send_all(self, data: List[dict]) -> List[dict]:
        raise NotImplementedError

    def initialize(self):
        pass

    def dispose(self):
        pass
