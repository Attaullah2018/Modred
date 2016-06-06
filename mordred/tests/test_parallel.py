from mordred import Calculator, all_descriptors
from mordred.error import MissingValue
from rdkit.Chem import AllChem as Chem
from numpy.testing import assert_almost_equal
from nose.tools import eq_
import pickle


def test_parallel():
    calc = Calculator(all_descriptors())
    mols = list(map(Chem.AddHs, [
        Chem.MolFromSmiles('c1ccccc1'),
        Chem.MolFromSmiles('C1=CC(=C(C=C1C2=C(C=C3C(=CC(=CC3=[O+]2)O)O)O)O)O'),
        Chem.MolFromSmiles('CCCCCC'),
    ]))

    for mol in mols:
        Chem.EmbedMolecule(mol)

    for (_, serial), (_, parallel) in zip(calc.map(mols, nproc=1, quiet=True),
                                          calc.map(mols, quiet=True)):
        for d, s, p in zip(calc.descriptors, serial, parallel):
            if isinstance(s, MissingValue):
                yield eq_, pickle.dumps(s), pickle.dumps(p), str(d)
            else:
                yield assert_almost_equal, s, p, 7, str(d)
