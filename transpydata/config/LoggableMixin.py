from logging import Logger


class LoggableMixin():
    def __init__(self):
        super().__init__()
        self._logger = None # type: Logger

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, logger: Logger):
        self._logger = logger

