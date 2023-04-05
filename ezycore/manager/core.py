from __future__ import annotations
from abc import ABC, abstractmethod

from .segment import BaseSegment, Segment
from ezycore.models import Model
from ezycore.drivers import Driver

from typing import Any, List, Tuple, Dict, Iterable, Union, Optional


class BaseManager(ABC):
    """
    Standard manager class, all managers should inherit this class.

    Parameters
    ----------
    locations: List[Union[str, BaseSegment]]
        List of locations to manage
    models: Dict[:class:`str`, :class:`Model`]
        Models to intialise segments with, if segment already has model, model is overwritten
    location_data: Dict[:class:`str`, Dict[:class:`str`, Any]]
        Kwargs for defining segment if segment doesn't already exist. Meaning its being passed by string
    """
    @staticmethod
    @abstractmethod
    def __seg_cls():
        return BaseSegment
    

    def __init__(
        self,
        locations: List[Union[str, BaseSegment]],
        models: Dict[str, Model] = {},
        location_data: Dict[str, Dict[str, Any]] = dict()
    ) -> None:
        self.__locations: Dict[str, BaseSegment] = dict()
        self.__models: Dict[str, Model] = models

        self.__index: int = 0

        for v in locations:
            if type(v) == str:
                self.__locations[v] = self.__seg_cls()(**location_data.get(v, dict(name=v, model=self.__models.get(v))))
            elif not issubclass(v, BaseSegment):
                raise TypeError('Locations provided must be of type str or inherit BaseSegment class')
            else:
                self.__locations[v.name] = v

                self.replace_model(self.__locations[v.name], self.__models.get(v.name, v.model))
                self.__models[v.name] = v.model

            self.__locations[v]._set_manager(self)

        self.__k: Tuple[str] = tuple(self.__locations)

    def _modify_loc(self) -> dict:
        return self.__locations

    def _modify_mod(self) -> dict:
        return self.__models

    ###########################################################################################
    ##
    ## Generic Methods
    ##
    ###########################################################################################

    @abstractmethod
    def populate(self, location: str, *d, data: Iterable[Union[dict, Model]] = tuple()) -> None:
        """ Populate a segment with an array of data structs

        Parameters
        ----------
        location: :class:`str`
            Name of segment to populate
        data: Iterable[Union[:class:`dict`, :class:`Segment`]]
            Array of data to add
        """

    @abstractmethod
    def populate_using_driver(self, location: str, driver: Driver, **driver_kwargs) -> None:
        """ Populate a segment using a driver

        Parameters
        ----------
        location: :class:`str`
            Name of segment to populate
        driver: :class:`Driver`
            Driver to use
        **driver_kwargs:
            Additional kwargs for :meth:`Driver.fetch`
        """

    @abstractmethod
    def export_segment(self, location: str, driver: Driver = None, **driver_kwargs) -> None:
        """ Export a segment using a driver or any class which can handle a `export` method

        Parameters
        ----------
        location: :class:`str`
            Name of segment to export
        driver: :class:`Driver`
            Driver to use
        **driver_kwargs:
            Additional kwargs for :meth:`Driver.export`
        """

    ###########################################################################################
    ##
    ## Segments
    ##
    ###########################################################################################

    def segments(self) -> Iterable[BaseSegment]:
        """ Returns all segments assigned to manager """
        return iter(self.__locations.values())

    def get_segment(self, segment: str, *, defer: bool = False) -> Optional[BaseSegment]:
        """ Gets a saved segment, if deferred, returns `None` if segment doesn't exist.
            Else raises `KeyError`.

            Parameters
            ----------
            segment: :class:`str`
                Segment to get
            defer: :class:`bool`
                Whether to return `None` if segment not found
        """
        try:
            return self.__locations[segment]
        except KeyError as err:
            if defer:
                return
            raise KeyError('Segment not found') from err

    @abstractmethod
    def add_segment(self, segment: Union[str, BaseSegment], **kwds) -> None:
        """ Add a new segment to manager, 
            should raise `ValueError` if segment already exists

        Parameters
        ----------
        segment: Union[:class:`str`, :class:`BaseSegment`]
            Segment to add
        **kwds:
            If segment being added passed as string, additional kwargs to control creation
        """

    @abstractmethod
    def remove_segment(self, location: str) -> None:
        """ Removes an existing segment from manager,
            Should raise `ValueError` if segment doesn't exist

        Parameters
        ----------
        location: :class:`str`
            Name of segment to remove
        """

    @abstractmethod
    def update_segment(self, location: str, **data) -> BaseSegment:
        """ Updates an existing segment to handle new data

        Paramaters
        ----------
        location: :class:`str`
            Name of segment to update
        **data:
            See :meth:`BaseSegment.update` for more info
        """

    def replace_segment(self, segment: Union[str, BaseSegment], new_segment: Union[str, BaseSegment]) -> None:
        """ Replaces/Adds a segment regardless if segment already exists,
        WARNING: Inproper use may lead to unexpected errors.

        * If segment provided not found, new segment is created
        * If segment found, segment to be deleted and new segment is added

        Parameters
        ----------
        segment: Union[:class:`str`, :class:`BaseSegment`]
            Segment to replace
        new_segment: Union[:class:`str`, :class:`BaseSegment`]
            Segment to use instead of existing segment
        """
        try:
            self.remove_segment(getattr(segment, 'name', segment))
        except ValueError:
            pass
        self.add_segment(new_segment)

    ###########################################################################################
    ##
    ## Models
    ##
    ###########################################################################################

    def models(self) -> Iterable[Model]:
        """ Returns all models assigned to manager """
        return iter(self.__models.values())

    def get_model(self, location: str, *, defer: bool = False, skip_manager: bool = False) -> Optional[Model]:
        """ Retrieves a model being used by a segment.
            If deferred, returns `None` if model doesn't exist.
            Else raises `KeyError`.

        Parameters
        ----------
        location: :class:`str`
            Name of segment to retrieve model from
        defer: :class:`bool`
            Whether to return `None` if model not found
        skip_manager: :class:`bool`
            Whether to directly search segment instead of manager
        """

        if skip_manager:
            return self.get_segment(location).model
        try:
            return self.__models[location]
        except KeyError as err:
            if not defer:
                raise KeyError('Segment model not found') from err

    def replace_model(self, location: str, model: Model) -> None:
        """ Adds/Overwrites model to a segment.
            If model is None, then segment model is removed

        Parameters
        ----------
        location: :class:`str`
            Name of segment
        model: :class:`Model`
            Model to bind to segment
        """
        segment = self.get_segment(location)
        segment.update_segment(model=model)

    ###########################################################################################
    ##
    ## Other Methods
    ##
    ###########################################################################################

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(locations={self.__k})"

    def __getitem__(self, segment: str) -> Segment:
        try:
            return self.__locations[segment]
        except KeyError as err:
            raise KeyError("Segment not found") from err

    def __setitem__(self, segment: str, new_segment: Union[str, Segment]) -> None:
        self.replace_segment(segment, new_segment)

    def __delitem__(self, segment: str) -> None:
        self.remove_segment(segment)

    def __contains__(self, segment: str) -> None:
        assert type(segment) == str, f"Cannot compare str with {type(segment).__name__}"
        return segment in self.__locations

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return


    def __iter__(self):
        return self

    def __next__(self):
        self.__index += 1
        if self.__index > len(self.__k):
            self.__index = 0
            return self.__k[-1]
        return self.__k[self.__index - 1]

########################################################################
##                                                                    ##
##                      DEFAULT IMPLMENTATION                         ##
##                                                                    ##
########################################################################


class Manager(BaseManager):
    """ Default manager class implementation

    Parameters
    ----------
    locations: List[Union[str, BaseSegment]]
        List of locations to manage
    models: Dict[:class:`str`, :class:`Model`]
        Models to intialise segments with, if segment already has model, model is overwritten
    location_data: Dict[:class:`str`, Dict[:class:`str`, Any]]
        Kwargs for defining segment if segment doesn't already exist. Meaning its being passed by string
    """

    @staticmethod
    def _BaseManager__seg_cls():
        return Segment

    ###########################################################################################
    ##
    ## Generic Methods
    ##
    ###########################################################################################

    def populate(self, location: str, *d, data: Iterable[Union[dict, Model]] = tuple()) -> None:
        d = tuple(data) + d
        seg = self.get_segment(location)

        for loc in d:
            seg.add(loc)

    def populate_using_driver(self, location: str, driver: Driver, **driver_kwargs) -> None:
        seg = self.get_segment(location)

        if not driver_kwargs.get('model'):
            driver_kwargs['model'] = seg.model

        for loc in driver.fetch(**driver_kwargs):
            seg.add(loc)

    def export_segment(self, location: str, driver: Driver = None, **driver_kwargs) -> None:
        seg = self.get_segment(location)

        driver.export(seg, **driver_kwargs)

    ###########################################################################################
    ##
    ## Segments
    ##
    ###########################################################################################

    def add_segment(self, segment: Union[str, Segment], **kwds) -> None:
        seg_name = getattr(segment, 'name', segment)

        assert type(seg_name) == str
        if self.get_segment(seg_name, defer=True):
            raise ValueError('Segment already exists')

        if (type(segment) == str):
            self.__locations[seg_name] = Segment(kwds + {'name': seg_name})
        else:
            self.__locations[seg_name] = segment
        self.__k = tuple(self.__locations)

    def remove_segment(self, location: str) -> Segment:
        if location not in self.__locations:
            raise ValueError('Segment not found')
        
        rv = self.__locations.pop(location)
        self.__k = tuple(self.__locations)
        return rv

    def update_segment(self, location: str, **data) -> Segment:
        segment = self.get_segment(location)
        segment.update_segment(**data)
