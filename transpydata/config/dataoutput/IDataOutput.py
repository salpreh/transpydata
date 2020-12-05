from typing import List
from abc import ABCMeta, abstractmethod


class IDataOutput(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        pass #TODO: Add method checks

    @abstractmethod
    def configure(self, config: dict):
        raise NotImplementedError

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
