import logging
from typing import Type, Union, List

from clinlog.logging import get_logger

from transpydata.config import IProcessor, IResourceAware
from transpydata.config.datainput.IDataInput import IDataInput
from transpydata.config.dataprocess.IDataProcess import IDataProcess
from transpydata.config.dataoutput.IDataOutput import IDataOutput



class TransPy():

    DATAINPUT_PROC_ID = 'datainput'
    DATAPROCESS_PROC_ID = 'dataprocess'
    DATAOUTPUT_PROC_ID = 'dataoutput'


    def __init__(self):
        self.logger = None
        self.log_level = logging.INFO

        self.datainput = None # type: IDataInput
        self.dataprocess = None # type: IDataProcess
        self.dataoutput = None # type: IDataOutput

        self._datainput_by_one = False
        self._dataprocess_by_one = False
        self._dataoutput_by_one = False

        self._dataservices_init = self._default_dataservices_init()

        self._datainput_source = []

    def configure(self, config: dict):
        self._datainput_by_one = config.get('datainput_by_one',
                                            self._datainput_by_one)
        self._datainput_source = config.get('datainput_source',
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
        if self._datainput_by_one:
            processed_data = self._single_processing_pipe(self._datainput_source,
                                                          self._datainput_by_one,
                                                          self._dataprocess_by_one,
                                                          self._dataoutput_by_one)
        else:
            processed_data = self._exec_process(self.datainput, False,
                                                self.DATAINPUT_PROC_ID)

        self._dispose_dataservice(self.datainput, self.DATAINPUT_PROC_ID)

        # Process data
        if not self._datainput_by_one and self._dataprocess_by_one:
            processed_data = self._single_processing_pipe(processed_data,
                                                          self._datainput_by_one,
                                                          self._dataprocess_by_one,
                                                          self._dataoutput_by_one)
        elif not self._dataprocess_by_one:
            processed_data = self._exec_process(self.dataprocess, False,
                                                self.DATAPROCESS_PROC_ID,
                                                processed_data)

        self._dispose_dataservice(self.dataprocess, self.DATAPROCESS_PROC_ID)

        # Send data to output
        if not self._dataprocess_by_one and self._dataoutput_by_one:
            processed_data = self._single_processing_pipe(processed_data,
                                                          False,
                                                          False,
                                                          self._dataoutput_by_one)
        elif not self._dataoutput_by_one:
            processed_data = self._exec_process(self.dataoutput, False,
                                                self.DATAOUTPUT_PROC_ID,
                                                processed_data)

        self._dispose_dataservice(self.dataoutput, self.DATAOUTPUT_PROC_ID)

        return processed_data

    def _single_processing_pipe(self, input_data: list, datainput_by_one: bool,
                                dataprocess_by_one: bool, dataoutput_by_one: bool):
        collected_data = []
        piped_data = None
        for input_datum in input_data:
            piped_data = input_datum

            if datainput_by_one:
                piped_data = self._exec_process(self.datainput,
                                                datainput_by_one,
                                                self.DATAINPUT_PROC_ID,
                                                piped_data)

            if dataprocess_by_one:
                piped_data = self._exec_process(self.dataprocess,
                                                dataprocess_by_one,
                                                self.DATAPROCESS_PROC_ID,
                                                piped_data)

            if datainput_by_one and not dataprocess_by_one:
                collected_data.append(piped_data)
                continue

            if dataoutput_by_one:
                piped_data = self._exec_process(self.dataoutput,
                                                dataoutput_by_one,
                                                self.DATAOUTPUT_PROC_ID,
                                                piped_data)

            collected_data.append(piped_data)

        return collected_data

    def _exec_process(self, processor: IProcessor,
                      process_by_one: bool, dataprocessor_id: str,
                      process_input: Union[dict,list]=None) -> Union[dict,list]:

        if (not self._dataservices_init[dataprocessor_id]
            and isinstance(processor, IResourceAware)):
            processor.initialize()
            self._dataservices_init[dataprocessor_id] = True

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
        if not isinstance(self.datainput, IDataInput):
            self._raise_processor_not_implemented(self.datainput, IDataInput)

        if not isinstance(self.dataprocess, IDataProcess):
            self._raise_processor_not_implemented(self.dataprocess, IDataProcess)

        if not isinstance(self.dataoutput, IDataOutput):
            self._raise_processor_not_implemented(self.dataoutput, IDataOutput)

    def _dispose_dataservices(self):
        self._dispose_dataservice(self.datainput, self.DATAINPUT_PROC_ID)
        self._dispose_dataservice(self.dataprocess, self.DATAPROCESS_PROC_ID)
        self._dispose_dataservice(self.dataoutput, self.DATAOUTPUT_PROC_ID)

    def _dispose_dataservice(self, dataservice: IResourceAware,
                             dataservice_id: str):
        if self._dataservices_init[dataservice_id]:
            dataservice.dispose()
            self._dataservices_init[dataservice_id] = False

    def _raise_processor_not_implemented(self, datainput, cls: Type):
            raise RuntimeError(
                "'{}' class does not implement methods or inherit from class '{}'"
                .format(datainput.__class__.__name__,
                        cls.__name__)
            )

    def _default_dataservices_init(self) -> dict:
        return {
            self.DATAINPUT_PROC_ID: False,
            self.DATAPROCESS_PROC_ID: False,
            self.DATAOUTPUT_PROC_ID: False
        }
