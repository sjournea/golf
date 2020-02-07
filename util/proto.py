"""proto.py - abstract data model class."""
from abc import ABCMeta, abstractmethod


class Proto:
    """Abstract base class."""

    __metaclass__ = ABCMeta

    def validate(self):
        pass

    @abstractmethod
    def fromDict(self, dct):
        pass

    @abstractmethod
    def toDict(self):
        pass

    @classmethod
    def initFromDict(cls, dct):
        p = cls.__new__(cls)
        p.fromDict(dct)
        return p
