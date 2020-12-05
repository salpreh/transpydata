from typing import List
from abc import ABCMeta, abstractmethod


class IDataInput(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        pass #TODO: Add method checks

    @abstractmethod
    def configure(self, config):
        raise NotImplementedError

    @abstractmethod
    def get_one(self, params: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> List[dict]:
        raise NotImplementedError

    def initialize(self):
        pass

    def dispose(self):
        pass
