import unittest
from abc import ABCMeta, abstractmethod

from transpydata.util.decorators import duckyinterface

class TestDecorators(unittest.TestCase):
    def test_duckyinterface(self):
        # Ducky interface
        @duckyinterface
        class Interface(metaclass=ABCMeta):
            @abstractmethod
            def interface_m(self):
                raise NotImplementedError

        # Class implementig interface
        class ImpClass(Interface):
            def interface_m(self):
                return 'implemented'

        # Ducky typing class
        class DuckyClass():
            def interface_m(self):
                return 'implemented'

        imp_class = ImpClass()
        ducky_class = DuckyClass()

        self.assertTrue(isinstance(imp_class, Interface))
        self.assertTrue(isinstance(ducky_class, Interface))
