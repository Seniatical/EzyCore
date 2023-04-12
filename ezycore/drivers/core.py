from __future__ import annotations
from abc import ABC, abstractmethod

from typing import Any, Dict, Iterator, Optional, Tuple, Union
from typing_extensions import TypeAlias
from os import PathLike

from ezycore.models import Model


# Iterator class used to accomodate varying data structs such as SQLs tuples
RESULT = Union[Dict[str, Any], Model, Tuple[Any]]
StrOrBytesPath: TypeAlias = Union[str, bytes, PathLike[str], PathLike[bytes]]  


class Driver(ABC):
    """ Base class for defining custom drivers """

    @abstractmethod
    def fetch(self, location: str, condition: Any = None, limit_result: int = -1, 
              model: Model = None, *, raw: Any = None, no_handle: bool = False, ignore_model: bool = False,
              **kwds
    ) -> Iterator[RESULT]:
        """ Fetches as many results as possible based of query given

        Parameters
        ----------
        location: :class:`str`
            Place to fetch data from, varies between drivers.
        condition: Any
            Filter data based on a condition, varies between drivers.
        limit_result: :class:`int`
            Limit how many results are returned,
            if < 0, no limit is set
        model: :class:`Model`
            Model to return data as, 
            if no model binded to location, this model becomes the default
        raw: Any
            Raw query data instead of using an auto generated one,
            allows flexibility for some drivers such SQL based drivers
        no_handle: :class:`bool`
            Whether to just return the raw fetched data
        ignore_model: :class:`bool`
            Whether to return data as dict instead of model
        **kwds:
            Additional kwargs may be provided by other drivers which may require any
        """

    @abstractmethod
    def fetch_one(self, location: str, condition: Any = None, model: Model = None, 
                  *, raw: Any = None, no_handle: bool = False, ignore_model: bool = False,
                  **kwds
    ) -> Optional[RESULT]:
        """ Fetches only one result which matches the query

        Parameters
        ----------
        location: :class:`str`
            Place to fetch data from, varies between drivers.
        condition: Any
            Filter data based on a condition, varies between drivers.
        limit_result: :class:`int`
            Limit how many results are returned,
            if < 0, no limit is set
        model: :class:`Model`
            Model to return data as, 
            if no model binded to location, this model becomes the default
        raw: Any
            Raw query data instead of using an auto generated one,
            allows flexibility for some drivers such SQL based drivers
        no_handle: :class:`bool`
            Whether to just return the raw fetched data
        ignore_model: :class:`bool`
            Whether to return data as dict instead of model
        **kwds:
            Additional kwargs may be provided by other drivers which may require any
        """

    @abstractmethod
    def map_to_model(self, **kwds) -> None:
        """ Maps locations to internal data spots.

        e.g. Segment may be called `users`, but SQL table may be called `user_table`

        Parameters
        ----------
        **kwds:
            Keyword arguments for mapping from in-program name to database name.
            
            .. code-block:: py
            
                d = Driver(..., models={'users': UserModel})
                d.map_to_model(users='my_table')
        """

    @abstractmethod
    def export(self, location: str, stream: Iterator[Union[dict, Model]], include: set, exclude: set) -> None:
        """ Exports data from any object supporting the `__next__` method

        Parameters
        ----------
        location: str
            Location to export data to
        stream: Iterator[Union[:class:`dict`, :class:`Model`]]
            An object which returns values to export
        include: :class:`set`
            set of IDs to include
        exclude: :class:`set`
            set of IDs to exclude
        """
