from __future__ import annotations

from pydantic import BaseModel
from ezycore.exceptions import ModalMissingConfig


class Config(BaseModel):
    search_by: str
    allow_partial: bool = False
    allow_regex: bool = False


class Model(BaseModel):

    ## Ensures _config var exists
    def __init_subclass__(cls) -> None:
        try:
            r = getattr(cls, '_config')
        except AttributeError as err:
            raise ModalMissingConfig('_config variable not found') from err
        assert isinstance(r, Config), 'Invalid config class provided'

        return super().__init_subclass__()
