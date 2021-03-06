"""db_connect.py"""
from abc import ABC, abstractmethod, abstractproperty


class DBConnect(ABC):
    """Abstract base databse connection class."""

    def __init__(self, db, **kwargs):
        self.db = db

    @abstractmethod
    def databases(self, **kwargs):
        """Return dictionaries of database names with list of collection names. """
        pass

    @abstractmethod
    def drop_database(self, database=None):
        """Remove a database."""
        pass

    @abstractproperty
    def courses(self):
        return None

    @abstractproperty
    def players(self):
        return None

    @abstractproperty
    def rounds(self):
        return None
