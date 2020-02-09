"""proto.py - abstract data model class."""
from abc import ABC, abstractmethod


class Proto(ABC):
    """Abstract base class."""

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
