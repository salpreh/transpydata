from abc import ABCMeta
from logging import getLogger, Logger, NullHandler

from transpydata.config import (
    IConfigurable, IProcessor, IResourceAware, LoggableMixin
)
from transpydata.util.decorators import duckyinterface


class IDataService(IProcessor, IConfigurable, IResourceAware,
                   LoggableMixin, metaclass=ABCMeta):

    def __init__(self):
        super().__init__()

    def initialize(self):
        if self.logger is None or not isinstance(self.logger, Logger):
            self.logger = getLogger('dummy')
            self.logger.addHandler(NullHandler())
