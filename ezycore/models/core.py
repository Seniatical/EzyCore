from __future__ import annotations
from typing import Generic, Dict, Iterator, TypeVar

from pydantic import BaseModel, ValidationError
from pydantic.fields import ModelField
from ezycore.exceptions import ModalMissingConfig


class Config(BaseModel):
    search_by: str
    exclude: set = {'_config'}
    partials: Dict[str, str] = dict()


class Model(BaseModel, arbitrary_types_allowed=True):
    __ezycore_partials__: tuple = None

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
        type_ = field.outer_type_.__args__[0]

        if isinstance(v, type_):
            return v

        primary_key = type_._config.search_by

        primary_field =  type_.__fields__.get(primary_key)
        valid_value, err = primary_field.validate(v, {}, loc=primary_key)
        if err:
            raise ValidationError([err], cls)

        return valid_value
