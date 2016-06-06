from rdkit import Chem
from mordred import Descriptor, Calculator
from mordred.error import Error

from nose.tools import eq_


class RaiseDescriptor(Descriptor):
    def as_key(self):
        return self.__class__, ()

    def __init__(self, e, critical):
        self.e = e
        self.critical = critical

    def calculate(self):
        raise self.e


mol = Chem.MolFromSmiles('c1ccccc1')


def test_catch_non_critical_error():
    calc = Calculator(RaiseDescriptor(ValueError('test exception'), False))

    result = calc(mol)[0]
    assert isinstance(result, Error)
    eq_(result.error.args, ('test exception',))