from abc import ABCMeta, abstractmethod


class IResourceAware(metaclass=ABCMeta):
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def dispose(self):
        pass

