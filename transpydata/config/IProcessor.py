from abc import ABCMeta, abstractmethod


class IProcessor(metaclass=ABCMeta):
    @abstractmethod
    def process_one_method_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def process_all_method_name(self) -> str:
        raise NotImplementedError
