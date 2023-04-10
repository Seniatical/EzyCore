from __future__ import annotations
from abc import ABC, abstractmethod

from ezycore.models import Model, M
from ezycore.exceptions import Full, SegmentError
from typing import Any, Iterable, Optional, Union


class BaseSegment(ABC):
    """
    Base class for creating segments

    Parameters
    ----------
    name: :class:`str`
        Name of segment
    max_size: :class:`int`
        Maximum size of segment, if < 0 then size of segment is infinite
    model: :class:`Model`
        Model being used to store data
    make_space: :class:`bool`
        Whether to start removing content once segment is full starting from the piece of data last accessed
    """
    def __init__(
        self,
        name: str,
        model: Model,
        *,
        max_size: int = 1000,
        make_space: bool = True
    ) -> None:
        try:
            assert type(name) == str, 'Name of segment must be a string'
            assert issubclass(model, Model), 'modal provided must inherit the Modal class'
            assert type(max_size) == int, 'Max size must be an integer'
            assert type(make_space) == bool, 'Value for make space must be a boolean'
        except (AssertionError, TypeError) as err:
            raise SegmentError('Invalid args provided') from err


        self.__name = name
        self.__max_size = max_size
        self.__model = model
        self.__ms = make_space
        self.__manager = None

    def update_segment(self, 
               *,
               name: str = ...,
               max_size: int = ...,
               model: Model = ...,
               make_space: bool = ...
    ) -> None:
        """ Used to update enclosed variables in a segment

        Parameters
        ----------
        name: :class:`str`
            Name of segment
        max_size: :class:`int`
            Maximum size of segment, if < 0 then size of segment is infinite
        model: :class:`Model`
            Model being used to store data
        make_space: :class:`bool`
            Whether to start removing content starting from the piece of data last accessed
        """
        if model != ...:
            assert issubclass(model, Model), 'modal provided must inherit the Modal class'
            if self.__manager:
                __mod = self.__manager._modify_mod()
                __mod.pop(self.__name, None)
                __mod[self.__name] = model
            self.model = model

        if name != ...:
            assert type(name) == str, 'Name of segment must be a string'
            if self.__manager:
                __loc = self.__manager._modify_loc()
                __loc.pop(self.__name, None)
                __loc[name] = self

                __mod = self.__manager._modify_mod()
                _m = __mod.pop(self.__name, None)
                __mod[name] = _m
            self.__name = name

        if max_size != ...:
            assert type(max_size) == int, 'Max size must be an integer'
            self.__max_size = max_size
        if make_space != ...:
            assert type(make_space) == bool, 'Value for make space must be a boolean'
            self.__ms = make_space 
        
    def _set_manager(self, manager: Any) -> None:
        if not self.__manager:
            self.__manager = manager
        else:
            raise ValueError('Segment already set to manager')

    def _del_manager(self) -> None:
        if not self.__manager:
            raise ValueError('No manager set')
        self.__manager = None

    def _get_manager(self) -> Optional[Any]:
        return self.__manager

    ###########################################################################################
    ##
    ##  Properties
    ##
    ###########################################################################################

    @property
    def name(self) -> str:
        """ Returns name of segment """
        return self.__name
    
    @property
    def max_size(self) -> int:
        """ Returns maximum-size of segment """
        return self.__max_size
    
    @property
    def model(self) -> Model:
        """ Returns model of segment """
        return self.__model

    @property
    def make_space(self) -> bool:
        """ Whether model should remove least accessed data """
        return self.__ms

    ###########################################################################################
    ##
    ##  Methods
    ##
    ###########################################################################################

    @abstractmethod
    def size(self) -> int:
        """ Returns total number of elements in segment """

    @abstractmethod
    def keys(self) -> Iterable[Any]:
        """ Returns an iterator of all keys in segment """

    @abstractmethod
    def values(self) -> Iterable[Model]:
        """ Returns an iterator of all values in segment """

    @abstractmethod
    def get(self, obj_key: Any, *flags, default: Any = None) -> Optional[Model]:
        """ Retrieves an element from cache

        Parameters
        ----------
        obj_key: Any
            value to search for, set in `Model.__config__.search_by`
        """

    @abstractmethod
    def add(self, obj: Union[dict, Model], *, overwrite: bool = False) -> None:
        """ Adds an element within the segment,
            raises `ValueError` if object already exists unless overwrite set to `True`.

        Parameters
        ----------
        obj: Union[:class:`dict`, :class:`Model`]
            Object to add
        overwrite: :class:`bool`
            Whether to overwrite an existing element
        """

    @abstractmethod
    def remove(self, obj_key: Any, *default: Any) -> Optional[Model]:
        """ Removes an element from segment,
            raises `KeyError` if key doesn't exist unless default is provided

        Parameters
        ----------
        obj_key: Any
            Value of stored key to remove
        *default:
            If value not found, returns this instead of raising an error
        """

    @abstractmethod
    def update(self, obj_key: Any, **kwds) -> None:
        """ Updates an element in the segment

        Parameters
        ----------
        obj_key: Any
            Object key to update
        **kwds:
            Fields to update
        """

    @abstractmethod
    def last(self) -> Optional[Model]:
        """ Retrieves item which was last accessed """

    @abstractmethod
    def clear(self) -> None:
        """ Removes all elements from segment """ 

    @abstractmethod
    def pretty_print(self, *, limit: int = -1) -> None:
        """ Prints out all data in segment, or until specified limit

        Parameters
        ----------
        limit: :class:`int`
            How many rows to print out, starting from most request data
        """

    ###########################################################################################
    ##
    ##  Others
    ##
    ###########################################################################################

    def __iter__(self):
        return self

    @abstractmethod
    def __next__(self) -> Any:
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, size={self.size()}, max_size={self.max_size}, model={self.model})"

    def __len__(self) -> int:
        return self.size()


class Segment(BaseSegment):
    """
    Default segment class

    Parameters
    ----------
    name: :class:`str`
        Name of segment
    max_size: :class:`int`
        Maximum size of segment
    model: :class:`Model`
        Model being used to store data
    make_space: :class:`bool`
        Whether to start removing content starting from the piece of data last accessed
    """
    def __init__(
        self,
        name: str, 
        model: Model,
        *,
        max_size: int = 1000,
        make_space: bool = True
    ) -> None:
        super().__init__(name, model, max_size=max_size, make_space=make_space)

        self.__queue = list()
        self.__data = dict()
        self.__position = 0

    def size(self) -> int:
        return len(self.__data)

    def keys(self) -> Iterable[Any]:
        return iter(self.__data.keys())
    
    def values(self) -> Iterable[Model]:
        return iter(self.__data.values())

    def _get(self, obj_key: Any, *include, default: Any = None, **kwds) -> Optional[Model]:
        ## Simply retrieves value, no queue handling here
        try:
            data: Model = self.__data[obj_key]
            for partial in data.__ezycore_partials__:
                if not self.__manager:
                    break
                prim_key = getattr(data, partial)
                try:
                    setattr(data, partial, self.__manager[data._config.partials[partial]].get(prim_key))
                except ValueError:
                    pass

            if not include:
                return data
            if '*' in include:
                kwds.update({'exclude': kwds.get('exclude', set())})
                kwds['exclude'].add('config')
                return data.dict(**kwds)
            return data.dict(include=set(include), **kwds)
        except KeyError as err:
            if default:
                return default
            raise KeyError('object not found') from err

    def get(self, obj_key: Any, *flags, default: Any = ...) -> Optional[Model]:
        try:
            self.__queue.remove(obj_key)
        except ValueError as err:
            if default == ...:
                raise ValueError('Object not found') from err
            return default
        self.__queue.append(obj_key)

        return self._get(obj_key, *flags, default=default)

    def add(self, obj: M, *, overwrite: bool = False) -> None:
        assert isinstance(obj, (dict, self.model)), 'Invalid object passed'

        v = dict(obj)
        key = self.model._config.search_by

        if v[key] in self.__data and not overwrite:
            raise ValueError('Item already exists')

        if (len(self.__queue) >= self.max_size) and (self.max_size > 0):
            if not self.make_space:
                raise Full('Segment full')
            k = self.__queue.pop(0)
            self.__data.pop(k)
        self.__data[v[key]] = self.model(**v)
        self.__queue.append(v[key])

    def remove(self, obj_key: Any, *default: Any) -> Optional[Model]:
        try:
            self.get(obj_key)       ## Checks if item exists and brings item at the back of queue
        except KeyError as err:
            if default:
                return default[0] if len(default) == 1 else default
            raise err

        self.__queue.pop()
        self.__data.pop(obj_key)

    def update(self, obj_key: Any, **kwds) -> None:
        current = self.get(obj_key)
        d = dict(current)
        d.update(kwds)

        self.__data[obj_key] = self.model(**d)

    def last(self) -> Optional[Model]:
        if self.size() == 0:
            return
        return self.__data[self.__queue[-1]]

    def clear(self) -> None:
        self.__position = 0
        self.__data.clear()
        self.__queue.clear()

    def pretty_print(self, *, limit: int = -1) -> None:
        if (limit < 0) or (limit > self.size()):
            limit = self.size()
        
        headers = []
        for field in self.model.__fields__:
            headers.append(field)
        print('\t'.join(headers))

        for i in range(limit):
            key = self.__queue[-1 - i]
            obj = self.__data[key]

            for header in headers:
                print(getattr(obj, header), end='\t')
            print()
        print()

    def __iter__(self):
        self.__position = 0
        return super().__iter__()

    def __next__(self) -> Model:
        if self.__position >= self.size():
            self.__position = 0
            raise StopIteration
        self.__position += 1
        return self.__data[self.__queue[-1 - (self.__position - 1)]]
