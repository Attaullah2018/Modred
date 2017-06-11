import os
import warnings
import numpy as np

from importlib import import_module
from ..error import MissingValueBase

from .descriptor import Descriptor, UnaryOperatingDescriptor, ConstDescriptor, BinaryOperatingDescriptor
from .calculator import Calculator, get_descriptors_from_module
from .parallel import parallel


__all__ = (
    'all_descriptors',
    'Descriptor',
    'Calculator',
    'get_descriptors_from_module',
    'is_missing',
)


def all_descriptors():
    r"""**[deprecated]** use mordred.descriptors module instead.

    yield all descriptor modules.

    :returns: all modules
    :rtype: :py:class:`Iterator` (:py:class:`Descriptor`)
    """
    warnings.warn('all_descriptors() is deprecated, use mordred.descriptors module instead', DeprecationWarning, stacklevel=2)
    base_dir = os.path.dirname(os.path.dirname(__file__))

    for name in os.listdir(base_dir):
        name, ext = os.path.splitext(name)
        if name[:1] == '_' or ext != '.py' or name == 'descriptors':
            continue

        yield import_module('..' + name, __package__)


def _Descriptor__call__(self, mol, id=-1):
    r"""calculate single descriptor value.
    :type id: int
    :param id: conformer id

    :returns: descriptor result
    :rtype: scalar
    """
    v = Calculator(self)(mol, id)[0]
    if isinstance(v, MissingValueBase):
        raise v.error

    return v


def _from_json(obj, descs):
    name = obj.get('name')
    args = obj.get('args') or {}
    if name is None:
        raise ValueError('invalid json: {}'.format(obj))

    if name == UnaryOperatingDescriptor.__name__:
        return UnaryOperatingDescriptor(
            args['name'],
            args['operator'],
            _from_json(args['value'])
        )

    elif name == BinaryOperatingDescriptor.__name__:
        return BinaryOperatingDescriptor(
            args['name'],
            args['operator'],
            _from_json(args['left']),
            _from_json(args['right'])
        )

    cls = descs.get(name)
    if cls is None:
        raise ValueError('unknown class: {}'.format(name))

    instance = cls(**(obj.get('args') or {}))
    return instance


@classmethod
def _Descriptor_from_json(self, obj):
    '''create Descriptor instance from json dict.

    Parameters:
        obj(dict): descriptor dict

    Returns:
        Descriptor: descriptor
    '''
    descs = getattr(self, '_all_descriptors', None)

    if descs is None:
        from mordred import descriptors
        descs = {
            cls.__name__: cls
            for cls in get_descriptors_from_module(descriptors, submodule=True)
        }
        descs[ConstDescriptor.__name__] = ConstDescriptor
        self._all_descriptors = descs

    return _from_json(obj, descs)


def is_missing(v):
    '''check argument is either MissingValue or not

    Parameters:
        v(any): value

    Returns:
        bool
    '''
    return isinstance(v, MissingValueBase)


Descriptor.__call__ = _Descriptor__call__
Descriptor.from_json = _Descriptor_from_json
Calculator._parallel = parallel
