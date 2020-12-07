from abc import ABCMeta, abstractmethod


class IConfigurable(metaclass=ABCMeta):
    @abstractmethod
    def configure(self, config):
        raise NotImplementedError

