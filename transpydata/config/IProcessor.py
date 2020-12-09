from abc import ABCMeta, abstractmethod


class IProcessor(metaclass=ABCMeta):
    @abstractmethod
    def process_one_method_name(self) -> str:
        """ Name of method used to process one record.

        Returns:
            str: Method name
        """
        raise NotImplementedError

    @abstractmethod
    def process_all_method_name(self) -> str:
        """ Name of method used to process all records.

        Returns:
            str: Method name
        """
        raise NotImplementedError
