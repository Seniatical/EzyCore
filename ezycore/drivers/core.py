from __future__ import annotations
from abc import ABC, abstractmethod

from typing import Any, Dict, Iterator, Optional, Union

from ezycore.models import Model
from ezycore.manager import Segment


# Iterator class used to accomodate varying data structs such as SQLs tuples
RESULT = Union[Dict[str, Any], Model, Iterator]


class Driver(ABC):
    """ Base class for defining custom drivers """

    @abstractmethod
    def fetch(self, query: Any, location: str = None, limit_result: int = -1, model: Model = None) -> Iterator[RESULT]:
        """ Fetches as many results as possible based of query given

        Parameters
        ----------
        query: Any
            Query for filtering data
        location: :class:`str`
            Name were data is being stored,
            may vary between drivers
        limit_result: :class:`int`
            Number of results to limit to, 
            values < 0 returns everything found
        model: :class:`Model`
            Model to convert results to,
            if no model present returns raw result
        """

    @abstractmethod
    def fetch_one(self, query: Any, location: str = None, model: Model = None) -> Optional[RESULT]:
        """ Fetches only one result which matches the query

        Parameters
        ----------
        query: Any
            Query for filtering data
        location: :class:`str`
            Name were data is being stored,
            may vary between drivers
        model: :class:`Model`
            Model to convert results to,
            if no model present returns raw result
        """

    @abstractmethod
    def export(self, segment: Segment, include: set, exclude: set) -> None:
        """ Exports data from segment

        Parameters
        ----------
        segment: :class:`Segment`
            Segment to export
        include: :class:`set`
            set of IDs to include
        exclude: :class:`set`
            set of IDs to exclude
        """

    @abstractmethod
    def refresh(self) -> None:
        """ Re-establishes connection to object """
