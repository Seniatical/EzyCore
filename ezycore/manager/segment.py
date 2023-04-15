from __future__ import annotations
from abc import ABC, abstractmethod

from ezycore.models import Model, M
from ezycore.exceptions import Full, SegmentError
from typing import Any, Callable, Iterable, Optional, Union
from re import _compile


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
            self.__model = model

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
    def get(self, obj_key: Any, *flags, default: Any = ..., **export_kwds) -> Optional[Model]:
        """ Retrieves an element from cache

        Parameters
        ----------
        obj_key: Any
            value to search for, set in `Model._config.search_by`
        *flags
            elements to include in cache, read more in the :class:`Model`'s section
        default: Any
            default value if element not found
        **export_kwds:
            export kwargs, read more `here <https://docs.pydantic.dev/usage/exporting_models/>`_
        """

    @abstractmethod
    def search(self, func: Callable[[Model], bool], *fields, limit: int = -1, **export_kwds) -> Iterable[M]:
        """ Searches for elements matching query in cache

        Parameters
        ----------
        func: Callable[[:class:`Model`], :class:`bool`]
            Function which returns whether element is needed
        *fields
            List of fields to return from model
        limit: :class:`int`
            Number of results to restrict search to, 
            if < 0 no limit is set.
        **export_kwds:
            export kwargs, read more `here <https://docs.pydantic.dev/usage/exporting_models/>`_
        """

    @abstractmethod
    def search_using_re(self, expr: str, *fields, flags: int = 0, key: str = ..., limit: int = -1, **export_kwds) -> Iterable[M]:
        """Searches for elements using regular expressions

        .. warning::

            Converts all values to :class:`str` using the ``str()`` func

        Parameters
        ----------
        expr: :class:`str`
            Regular expression to use
        flags: :class:`int`
            Flags for expression
        *fields
            List of fields to return from model
        key: :class:`str`
            Name of field to use, defaults to :attr:`Config.search_by`
        limit: :class:`int`
            Number of results to restrict search to, 
            if < 0 no limit is set.
        **export_kwds:
            export kwargs, read more `here <https://docs.pydantic.dev/usage/exporting_models/>`_
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
    def invalidate_all(self, func: Callable[[Model], bool], *, limit: int = -1) -> Iterable[Model]:
        """ Invalidates all entries which match check function

        Parameters
        ----------
        func: Callable[[:class:`Model`], :class:`bool`]
            Function which indicates whether entry should be removed
        limit: :class:`int`
            Limit how many entries should be removed,
            if < 0 no limit is set
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
    def first(self) -> Optional[Model]:
        """ Retrieves the item which was most recently accessed """

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

        self._invalidated_last = False

    def size(self) -> int:
        return len(self.__data)

    def keys(self) -> Iterable[Any]:
        return iter(self.__data.keys())
    
    def values(self) -> Iterable[Model]:
        return iter(self.__data.values())

    def _get(self, obj_key: Any, *include, default: Any = None, 
             ignore: bool = False, original: bool = False, **export_kwds) -> Optional[Model]:
        ## Simply retrieves value, no queue/cache invalidation handling here
        try:
            data: Model = self.__data[obj_key]
            manager = self._get_manager()
            for partial in data.__ezycore_partials__:
                if not manager:
                    break
                prim_key = getattr(data, partial)
                try:
                    setattr(data, partial, manager[data._config.partials[partial]].get(prim_key))
                except ValueError:
                    pass
            
            if ignore:      
                return (data, data) if original else data

            if not (include or export_kwds or self.model._config.exclude):
                return (data, data) if original else data
            if '*' in include:
                if original:
                    return data.dict(), data   
                return data.dict()

            inc = dict()
            if include:
                for field in include:
                    if isinstance(field, str):
                        inc[field] = True
                    else:
                        inc[field[0]] = field[1]

            export_kwds['exclude'] = export_kwds.get('exclude', dict())
            export_kwds['include'] = export_kwds.get('include') or inc

            if isinstance(export_kwds['exclude'], set) and isinstance(data._config.exclude, set):
                return data.dict(include=inc, **export_kwds)
            elif isinstance(export_kwds['exclude'], set) and isinstance(data._config.exclude, dict):
                export_kwds['exclude'] = dict(**data._config.exclude)
                for field in export_kwds['exclude']:
                    export_kwds['exclude'][field] = True
            else:
                for field in data._config.exclude:
                    export_kwds['exclude'][field] = True
            
            if not export_kwds['include']:      export_kwds.pop('include')
            if not export_kwds['exclude']:      export_kwds.pop('exclude')

            if original:
                return data.dict(**export_kwds), data
            return data.dict(**export_kwds)

        except KeyError as err:
            if default:
                return default
            raise KeyError('object not found') from err

    def get(self, obj_key: Any, *flags, default: Any = ..., **export_kwds) -> Optional[Model]:
        _ignore_q = export_kwds.pop('ignore_queue', False)
        
        if not _ignore_q:
            try:
                self.__queue.remove(obj_key)
            except ValueError:
                if default == ...:
                    raise ValueError('Object not found')
                return default
            self.__queue.append(obj_key)
        value, result = self._get(obj_key, *flags, original=True, default=default, **export_kwds)

        max_fetches = result._config.invalidate_after
        if max_fetches < 0:
            self._invalidated_last = False
            return value

        fetches = result._config.__ezycore_internal__['n_fetch'] + 1
        if fetches >= max_fetches:
            self._invalidated_last = True
            self.remove(obj_key)
        else:
            self._invalidated_last = False
            result._config.__ezycore_internal__['n_fetch'] = fetches
        return value

    def search(self, func: Callable[[Model], bool], *fields, limit: int = -1, **export_kwds) -> Iterable[M]:
        export_kwds.update(ignore_queue=True)
        results = list()
        for key in self.__queue:
            if len(results) >= limit and limit > 0:
                break
            works = func(self._get(key, ignore=True))
            if not works:
                continue
            results.append(self.get(key, *fields, **export_kwds))
        return results

    def search_using_re(self, expr: str, *fields, flags: int = 0, key: str = None, limit: int = -1, **export_kwds) -> Iterable[M]:
        export_kwds.update(ignore_queue=True)
        results = list()
        search_key = key or self.model._config.search_by
        re = _compile(expr, flags)

        for key in self.__queue:
            if len(results) >= limit and limit > 0:
                break
            works = re.match(str(getattr(self._get(key, ignore=True), search_key)))
            if not works:
                continue
            results.append(self.get(key, *fields, **export_kwds))
        return results

    def add(self, obj: M, *, overwrite: bool = False) -> None:
        assert isinstance(obj, (dict, self.model)), 'Invalid object passed'
        if isinstance(obj, self.model):
            obj._config.__ezycore_internal__['n_fetch'] = 0

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
            i = self.__queue.index(obj_key)
        except ValueError as err:
            if default:
                return default[0] if len(default) == 1 else default
            raise err
        self.__queue.pop(i)
        r = self.__data.pop(obj_key)

        return r

    def invalidate_all(self, func: Callable[[Model], bool], *, limit: int = -1) -> Iterable[Model]:
        values = list()
        for key in self.__queue:
            if len(values) >= limit and limit > 0:
                break
            works = func(self._get(key, ignore=True))
            if works:
                values.append(key)
        return [self.remove(i) for i in values]

    def update(self, obj_key: Any, **kwds) -> None:
        current = self.get(obj_key)
        d = dict(current)
        d.update(kwds)

        self.__data[obj_key] = self.model(**d)

    def first(self) -> Optional[Model]:
        if self.size() == 0:
            return
        return self.__data[self.__queue[-1]]

    def last(self) -> Optional[Model]:
        if self.size() == 0:
            return
        return self.__data[self.__queue[0]]

    def oldest(self, limit: int = -1) -> Iterable[Model]:
        """ Retrieves elements starting from the least accessed values

        Parameters
        ----------
        limit: :class:`int`
            How many elements to retrieve,
            if < 0 then all elements are retrieved
        """
        limit = limit if limit > 0 else self.size()
        for i in range(limit):
            yield self.__data[self.__queue[i]]
    
    def newest(self, limit: int = -1) -> Iterable[Model]:
        """ Retrieves elements starting from the most recently accessed values

        Parameters
        ----------
        limit: :class:`int`
            How many elements to retreive,
            if < 0 then all elements are retrieved
        """
        limit = limit if limit > 0 else self.size()
        for i in range(limit):
            yield self.__data[self.__queue[-1 - i]]

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

    def __iter__(self, *, position: int = 0):
        self.__position = position
        return super().__iter__()

    def __next__(self) -> Model:
        if self.__position >= self.size():
            self.__position = 0
            raise StopIteration
        self.__position += 1
        return self.__data[self.__queue[-1 - (self.__position - 1)]]
