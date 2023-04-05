class Full(Exception):
    """ Raised when a segment no longer has any space left """


class ModalMissingConfig(Exception):
    """ Raised when model being used doesn't contain a ``_config`` var """
