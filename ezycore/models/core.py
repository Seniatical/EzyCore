from __future__ import annotations
from typing import Generic, Dict, Iterator, TypeVar, Union

from pydantic import BaseModel, ValidationError
from pydantic.fields import ModelField
from ezycore.exceptions import ModalMissingConfig


class Config(BaseModel):
    """\
    Configuration class used by the ezycore module. 
    Used to customise and control how ezycore behaves with segments and models

    Parameters
    ----------
    search_by: :class:`str`
        Which key to store as the primary key

        .. warning::
            This field **MUST** be **UNIQUE**
    exclude: Union[:class:`dict`, :class:`set`]
        Fields to exclude from being returned when being fetched
    partials: Dict[:class:`str`, :class:`str`]
        Mapping of partial vars to segment names.
    invalidate_after: :class:`int`
        Automatically invalidates entry after it is fetched n times
    """
    search_by: str
    exclude: Union[dict, set] = set()
    partials: Dict[str, str] = dict()
    invalidate_after: int = -1

    __ezycore_internal__: dict = {'n_fetch': 0}


class Model(BaseModel):
    __ezycore_partials__: tuple = None
    _config: Config

    def _read_partials(cls) -> Iterator[str]:
        for k, v in cls.__annotations__.items():
            __origin__ = getattr(v, '__origin__', None)
            if __origin__ == PartialRef:
                if issubclass(v.__args__[0], Model):
                    yield k
                else:
                    raise ValueError(f'Invalid model provided for partial definition: {k}')

    def _verify_partials(cls) -> None:
        partials = tuple(Model._read_partials(cls))
        cls.__ezycore_partials__ = partials

        defined_partials = cls._config.partials

        missing = []
        for i in partials:
            if i not in defined_partials:
                missing.append(i)
        if missing:
            raise ValueError('Missing partial definitions for: {}'.format(', '.join(missing)))


    ## Ensures _config var exists
    def __init_subclass__(cls, **kwds) -> None:
        try:
            r = getattr(cls, '_config')
        except AttributeError as err:
            raise ModalMissingConfig('_config variable not found') from err

        if isinstance(r, dict):
            setattr(cls, '_config', Config(**r)) 
        else:
            assert isinstance(r, Config), 'Invalid config class provided'
        Model._verify_partials(cls)
        return super().__init_subclass__(**kwds)


M = TypeVar('M', dict, Model)
_M = TypeVar('_M', bound=Model)


class PartialRef(Generic[_M]):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field: ModelField):
        type_: Model = field.outer_type_.__args__[0]

        if isinstance(v, type_):
            return v

        primary_key: str = type_._config.search_by

        primary_field: ModelField = type_.__fields__.get(primary_key)
        valid_value, err = primary_field.validate(v, {}, loc=primary_key)
        if err:
            raise ValidationError([err], cls)

        return valid_value
