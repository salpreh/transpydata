import logging
from typing import Type, Union, List

from transpydata.config import IProcessor
from transpydata.config.datainput.IDataInput import IDataInput
from transpydata.config.dataprocess.IDataProcess import IDataProcess
from transpydata.config.dataoutput.IDataOutput import IDataOutput

from clinlog.logging import get_logger


class TransPy():
    def __init__(self):
        self.logger = None
        self.log_level = logging.INFO

        self._datainput = None # type: IDataInput
        self._dataprocess = None # type: IDataProcess
        self._dataoutput = None # type: IDataOutput

        self._datainput_by_one = False
        self._dataprocess_by_one = False
        self._dataoutput_by_one = False

        self._datainput_source = []

    def configure(self, config: dict):
        self._datainput_by_one = config.get('datainput_by_one',
                                            self._datainput_by_one)
        self._datainput_by_one = config.get('datainput_source',
                                            self._datainput_source)
        self._dataprocess_by_one = config.get('dataprocess_by_one',
                                              self._dataprocess_by_one)
        self._dataoutput_by_one = config.get('dataoutput_by_one',
                                             self._dataprocess_by_one)

    def run(self) -> List[dict]:
        self._setup()
        self._processors_checks()

        # Get data input
        processed_data = []
        if self._dataprocess_by_one:
            processed_data = self._single_processing_pipe(self._datainput_source,
                                                          self._datainput_by_one,
                                                          self._dataprocess_by_one,
                                                          self._dataoutput_by_one)
        else:
            processed_data = self._exec_process(self._datainput, False)

        # Process data
        if not self._datainput_by_one and self._dataprocess_by_one:
            processed_data = self._single_processing_pipe(processed_data,
                                                          self._datainput_by_one,
                                                          self._dataprocess_by_one,
                                                          self._dataoutput_by_one)
        elif not self._dataprocess_by_one:
            processed_data = self._exec_process(self._dataprocess, False,
                                                processed_data)

        # Send data to output
        if not self._dataprocess_by_one and self._dataoutput_by_one:
            processed_data = self._single_processing_pipe(processed_data,
                                                          False,
                                                          False,
                                                          self._dataoutput_by_one)
        elif not self._dataoutput_by_one:
            processed_data = self._exec_process(self._dataoutput, False,
                                              processed_data)

        return processed_data

    def set_datainput(self, datainput: IDataInput):
        self._datainput = datainput

    def set_dataprocess(self, dataprocess: IDataProcess):
        self._dataprocess = dataprocess

    def set_dataoutput(self, dataoutput):
        self._dataoutput = dataoutput

    def _single_processing_pipe(self, input_data: list, datainput_by_one: bool,
                                dataprocess_by_one: bool, dataoutput_by_one: bool):
        collected_data = []
        piped_data = None
        for input_datum in input_data:
            piped_data = input_datum

            if datainput_by_one:
                piped_data = self._exec_process(self._datainput,
                                                datainput_by_one,
                                                piped_data)

            if dataprocess_by_one:
                piped_data = self._exec_process(self._dataprocess,
                                                dataprocess_by_one,
                                                piped_data)

            if datainput_by_one and not self._dataoutput_by_one:
                collected_data.append(piped_data)
                continue

            if dataoutput_by_one:
                piped_data = self._exec_process(self._dataoutput,
                                                dataoutput_by_one,
                                                piped_data)

            collected_data.append(piped_data)

        return collected_data

    def _exec_process(self, processor: IProcessor, process_by_one: bool,
                      process_input: Union[dict,list]=None) -> Union[dict,list]:
        process_m_name = processor.process_all_method_name()
        if process_by_one:
            process_m_name= processor.process_one_method_name()

        process_m = getattr(processor, process_m_name)

        if process_input is None:
            return process_m()

        return process_m(process_input)

    def _setup(self):
        if not self.logger:
            self.logger = get_logger()
        self.logger.setLevel(self.log_level)

    def _processors_checks(self):
        if not issubclass(self._datainput, IDataInput):
            self._raise_processor_not_implemented(self._datainput, IDataInput)

        if not issubclass(self._dataprocess, IDataProcess):
            self._raise_processor_not_implemented(self._dataprocess, IDataProcess)

        if not issubclass(self._dataoutput, IDataOutput):
            self._raise_processor_not_implemented(self._dataoutput, IDataOutput)

    def _raise_processor_not_implemented(self, datainput, cls: Type):
            raise RuntimeError(
                "'{}' class does not implement methods or inherit from class '{}'"
                .format(datainput.__class__.__name__,
                        cls.__name__)
            )
