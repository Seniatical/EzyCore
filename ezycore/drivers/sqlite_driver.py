from __future__ import annotations
from typing import Any, Dict, Iterator, Tuple, Type, Optional, Union
from sqlite3 import connect, Connection

from .core import Driver, RESULT, StrOrBytesPath
from ezycore.models import Model


class SQLiteDriver(Driver):
    """ Default implementation for the SQLite driver

    .. note::
        All paramaters not listed in the Parameters section may be found here,
        https://docs.python.org/3/library/sqlite3.html#sqlite3.connect

    Parameters
    ----------
    models: Dict[:class:`str`, :class:`Model`]
        Models to convert fetched results to, mapping must be table name to model
    model_maps: Dict[:class:`str`, :class:`str`]
        Mapping from model key to database table name
    """

    ## auto gen tables which we generally dont care about
    _IGNORE_LISTINGS = ('sqlite_sequence',)

    def __init__(self,
                 database: StrOrBytesPath,
                 timeout: float = 5.0,
                 detect_types: int = 0,
                 isolation_level: Union[str, None] = 'DEFERRED',
                 check_same_thread: bool = True,
                 factory: Union[Type[Connection], None] = Connection,
                 cached_statements: int = 128,
                 uri: bool = False,
                 cursorClass: Any = None,
                 models: Dict[str, Model] = dict(),
                 model_maps: Dict[str, str] = dict()
                ) -> None:
        self.__connection: Connection = connect(
            database=database,
            timeout=timeout,
            detect_types=detect_types,
            isolation_level=isolation_level,
            check_same_thread=check_same_thread,
            factory=factory,
            cached_statements=cached_statements,
            uri=uri
        )
        self.__cursor = self.__connection.cursor(**({'cursorClass': cursorClass} if cursorClass else {}))

        self.__models: Dict[str, Model] = models
        self.__headers: Dict[str, Tuple[str]] = dict()
        self.__maps: Dict[str, str] = model_maps
        self.__rev_map: Dict[str, str] = {v: k for k, v in self.__maps.items()}
        # table_name: (col, col, col)

        self._read_heads()

    def _read_heads(self) -> None:
        self.__cursor.execute('SELECT name FROM sqlite_master where type = "table"')
        for t_ in self.__cursor.fetchall():
            if (t_[0] in self._IGNORE_LISTINGS):
                continue
            self.__cursor.execute(f'SELECT * FROM {t_[0]} LIMIT 1')
            self.__headers[t_[0]] = tuple(i[0] for i in self.__cursor.description)

    def _result_to_output(self, head: str, model: Optional[Model], *results) -> Iterator[dict]:
        for result in results:
            data = {self.__headers[head][i]: v for i, v in enumerate(result)}
            if not model:
                yield data
            else:
                yield model(**data)

    def _get_model(self, location: str) -> Optional[Model]:
        # -> __models[loc] -> __models[__maps[loc]] -> __models[__rev_map[loc]]
        return self.__models.get(
            location, 
            self.__models.get(self.__maps.get(location), self.__models.get(self.__rev_map.get(location)))
        )

    def _model_fits(self, location: str) -> bool:
        model = self._get_model(location)
        if not model:
            return False
        keys = model.__fields__.keys()

        return set(self.__headers[location]).issubset(set(keys))

    def map_to_model(self, **kwds) -> None:
        self.__maps.update(kwds)
        self.__rev_map = {v: k for k, v in self.__maps.items()}


    def fetch(self, location: str, condition: str = '', limit_result: int = -1, 
              model: Model = None, *, raw: str = None, no_handle: bool = False, ignore_model: bool = False,
              parameters: Tuple[Any] = tuple()
    ) -> Optional[Iterator[RESULT]]:
        """
        Fetches data from a table

        Parameters
        ----------
        location: :class:`str`
            Table to fetch data from
        condition: Any
            Condition to use in ``WHERE`` statement,
            provide arg without the ``WHERE`` clause.
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
        parameters: Tuple[Any]
            Parameters to be supplied with statement, flexibility if using the ``raw`` arg
        """
        if model and not self._get_model(location):
            self.__models[location] = model
        model = self._get_model(location)
        table = self.__maps.get(location, location)

        if not raw:
            if condition:
                condition = f'WHERE {condition}'
            if limit_result > 0:
                limit_result = f'LIMIT {limit_result}'
            else:
                limit_result = ''
            raw = f'SELECT * FROM {table} {condition} {limit_result}'

        self.__cursor.execute(raw, parameters)
        res = self.__cursor.fetchall()

        if not res:     return
        if no_handle:   return iter(res)
        return self._result_to_output(table, model if not ignore_model else None, *res)


    def fetch_one(self, location: str, condition: Any = None, model: Model = None, 
                  *, raw: Any = None, no_handle: bool = False, ignore_model: bool = False,
                  parameters: Tuple[Any] = tuple()
    ) -> Optional[RESULT]:
        """
        Fetches only 1 item
        """
        if model and not self._get_model(location):
            self.__models[location] = model
        model = self._get_model(location)
        table = self.__maps.get(location, location)

        if not raw:

            if condition:
                condition = f'WHERE {condition}'
            raw = f'SELECT * FROM {table} {condition} LIMIT 1'

        self.__cursor.execute(raw, parameters)
        r = self.__cursor.fetchone()

        if not r:       return
        if no_handle:   return r
        return next(self._result_to_output(table, model if not ignore_model else None, r))


    def export(self, location: str, stream: Iterator[Union[dict, Model]]) -> None:
        assert self._model_fits(location), "Incorrect model or no model binded for this table"
        model = self._get_model(location)
        include = set(self.__headers[location])

        columns = []

        for data in stream:
            if isinstance(data, dict):
                if model:
                    data = model(**data)
            data = data.dict(include=include)
            columns.append(tuple(data.values()))

        v = ('?',) * len(include)
        self.__cursor.executemany(f'INSERT OR REPLACE INTO {location} VALUES ({",".join(v)})', columns)
