from typing import List

from .IDataProcess import IDataProcess

class NoneDataProcess(IDataProcess):
    """ A no operation data process. Will move the input from the DataIntput to
        DataOutput without changes. No need to configure.
    """
    def configure(self):
        pass
    def process_one(self, data: dict) -> dict:
        return data

    def process_all(self, data: List[dict]) -> List[dict]:
        return data
