from __future__ import annotations
from abc import ABC, abstractmethod

from typing import Any, Dict, Iterator, Optional, Union

from ezycore.models import Model
from ezycore.manager import Segment


RESULT = Union[Dict[str, Any], Model]


class Driver(ABC):
    """ Base class for defining custom drivers """

    @abstractmethod
    def fetch(self, query: Any, limit_result: int = -1, model: Model = None) -> Iterator[RESULT]:
        """ Fetches as many results as possible based of query given

        Parameters
        ----------
        query: Any
            Query for filtering data
        """

    @abstractmethod
    def fetch_one(self, *queries) -> Optional[RESULT]:
        """ Fetches only one result which matches the query

        Parameters
        ----------
        queries: Any
            Query args for filtering data, may vary between drivers.
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
