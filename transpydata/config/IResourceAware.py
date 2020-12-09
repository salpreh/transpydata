from abc import ABCMeta, abstractmethod


class IResourceAware(metaclass=ABCMeta):
    @abstractmethod
    def initialize(self):
        """ Method to initialize resources needed by the class.
        """
        pass

    @abstractmethod
    def dispose(self):
        """ Method to dispose resources acquired by the class.
        """
        pass

