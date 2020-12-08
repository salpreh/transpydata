from typing import Tuple
import unittest
import unittest.mock as mock


from transpydata.TransPy import TransPy
from transpydata.config.datainput.IDataInput import IDataInput
from transpydata.config.dataprocess.IDataProcess import IDataProcess
from transpydata.config.dataoutput.IDataOutput import IDataOutput

class TestTransPy(unittest.TestCase):

    def test_initialized_and_disposed(self):
        datainput, dataprocess, dataoutput = self._get_mocked_dataservices()

        trans_py = self._get_transpy_instance(datainput, dataprocess, dataoutput)

        trans_py.run()

        datainput.initialize.assert_called_once()
        datainput.dispose.assert_called_once()

        dataprocess.initialize.assert_called_once()
        dataprocess.dispose.assert_called_once()

        dataoutput.initialize.assert_called_once()
        dataoutput.dispose.assert_called_once()

    def test_batch_run(self):
        datainput, dataprocess, dataoutput = self._get_mocked_dataservices()
        datainput.get_all.return_value = ['dinA', 'dinB']
        dataprocess.process_all.return_value = ['dprA', 'dprB']
        dataoutput.send_all.return_value = ['doutA', 'doutB']

        config = {
            'datainput_by_one': False,
            'dataprocess_by_one': False,
            'dataoutput_by_one': False,
            'datainput_source': ['inA', 'inB']
        }

        trans_py = self._get_transpy_instance(datainput, dataprocess,
                                             dataoutput, config)

        result = trans_py.run()

        self.assertFalse(datainput.get_one.called,
                         'One item processing should not be called')
        datainput.get_all.assert_called_once()

        self.assertFalse(dataprocess.process_one.called,
                         'One item processing should not be called')
        dataprocess.process_all.assert_called_once_with(datainput.get_all.return_value)

        self.assertFalse(dataoutput.send_one.called,
                         'One item processing should not be called')
        dataoutput.send_all.assert_called_once_with(dataprocess.process_all.return_value)

        self.assertListEqual(result, dataoutput.send_all.return_value)

    def test_by_one_run(self):
        datainput, dataprocess, dataoutput = self._get_mocked_dataservices()

        datainput_returns = ['dinA', 'dinB']
        dataprocess_returns = ['dprA', 'dprB']
        dataoutput_returns = ['doutA', 'doutB']
        datainput.get_one.side_effect = datainput_returns
        dataprocess.process_one.side_effect = dataprocess_returns
        dataoutput.send_one.side_effect = dataoutput_returns

        config = {
            'datainput_by_one': True,
            'dataprocess_by_one': True,
            'dataoutput_by_one': True,
            'datainput_source': ['inA', 'inB']
        }

        trans_py = self._get_transpy_instance(datainput, dataprocess,
                                             dataoutput, config)

        result = trans_py.run()

        self.assertFalse(datainput.get_all.called,
                         'Batch processing should not be called')
        datainput.get_one.assert_any_call(config['datainput_source'][0])
        datainput.get_one.assert_any_call(config['datainput_source'][1])

        self.assertFalse(dataprocess.process_all.called,
                         'Batch processing should not be called')
        dataprocess.process_one.assert_any_call(datainput_returns[0])
        dataprocess.process_one.assert_any_call(datainput_returns[1])

        self.assertFalse(dataoutput.send_all.called,
                         'Batch processing should not be called')
        dataoutput.send_one.assert_any_call(dataprocess_returns[0])
        dataoutput.send_one.assert_any_call(dataprocess_returns[1])

        self.assertListEqual(result, dataoutput_returns)

    def test_input_and_process_by_one(self):
        datainput, dataprocess, dataoutput = self._get_mocked_dataservices()

        datainput_returns = ['dinA', 'dinB']
        dataprocess_returns = ['dprA', 'dprB']
        dataoutput_returns = ['doutA', 'doutB']
        datainput.get_one.side_effect = datainput_returns
        dataprocess.process_one.side_effect = dataprocess_returns
        dataoutput.send_all.return_value = dataoutput_returns

        config = {
            'datainput_by_one': True,
            'dataprocess_by_one': True,
            'dataoutput_by_one': False,
            'datainput_source': ['inA', 'inB']
        }

        trans_py = self._get_transpy_instance(datainput, dataprocess,
                                             dataoutput, config)

        result = trans_py.run()

        self.assertFalse(datainput.get_all.called,
                         'Batch processing should not be called')
        datainput.get_one.assert_any_call(config['datainput_source'][0])
        datainput.get_one.assert_any_call(config['datainput_source'][1])

        self.assertFalse(dataprocess.process_all.called,
                         'Batch processing should not be called')
        dataprocess.process_one.assert_any_call(datainput_returns[0])
        dataprocess.process_one.assert_any_call(datainput_returns[1])

        self.assertFalse(dataoutput.send_one.called,
                         'One item processing should not be called')
        dataoutput.send_all.assert_called_once_with(dataprocess_returns)

        self.assertListEqual(result, dataoutput_returns)



    def test_process_and_output_by_one(self):
        datainput, dataprocess, dataoutput = self._get_mocked_dataservices()

        datainput_returns = ['dinA', 'dinB']
        dataprocess_returns = ['dprA', 'dprB']
        dataoutput_returns = ['doutA', 'doutB']
        datainput.get_all.return_value = datainput_returns
        dataprocess.process_one.side_effect = dataprocess_returns
        dataoutput.send_one.side_effect = dataoutput_returns

        config = {
            'datainput_by_one': False,
            'dataprocess_by_one': True,
            'dataoutput_by_one': True,
            'datainput_source': ['inA', 'inB']
        }

        trans_py = self._get_transpy_instance(datainput, dataprocess,
                                             dataoutput, config)

        result = trans_py.run()

        self.assertFalse(datainput.get_one.called,
                         'One item processing should not be called')
        datainput.get_all.assert_called_once()

        self.assertFalse(dataprocess.process_all.called,
                         'Batch processing should not be called')
        dataprocess.process_one.assert_any_call(datainput_returns[0])
        dataprocess.process_one.assert_any_call(datainput_returns[1])

        self.assertFalse(dataoutput.send_all.called,
                         'Batch processing should not be called')
        dataoutput.send_one.assert_any_call(dataprocess_returns[0])
        dataoutput.send_one.assert_any_call(dataprocess_returns[1])

        self.assertListEqual(result, dataoutput_returns)


    def _get_mocked_dataservices(self) -> Tuple[mock.NonCallableMagicMock,
                                                mock.NonCallableMagicMock,
                                                mock.NonCallableMagicMock]:
        datainput = mock.create_autospec(IDataInput)
        datainput.process_one_method_name.return_value = 'get_one'
        datainput.process_all_method_name.return_value = 'get_all'

        dataprocess = mock.create_autospec(IDataProcess)
        dataprocess.process_one_method_name.return_value = 'process_one'
        dataprocess.process_all_method_name.return_value = 'process_all'

        dataoutput = mock.create_autospec(IDataOutput)
        dataoutput.process_one_method_name.return_value = 'send_one'
        dataoutput.process_all_method_name.return_value = 'send_all'

        return (datainput, dataprocess, dataoutput)

    def _get_transpy_instance(self, datainput, dataprocess,
                             dataoutput, config: dict = None) -> TransPy:
        trans_py = TransPy()
        trans_py.datainput = datainput
        trans_py.dataprocess = dataprocess
        trans_py.dataoutput = dataoutput

        if config is not None:
            trans_py.configure(config)

        return trans_py

