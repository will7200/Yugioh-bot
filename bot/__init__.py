import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
try:
    from bot.debug_helpers.logger import LastRecordHandler

    last_record = LastRecordHandler()
    logger.addHandler(last_record)
except ImportError:
    pass

logger.addHandler(ch)
logger.debug("Setup Complete")
from ._version import get_versions

__version__ = get_versions()['version']
if '+' in __version__:
    clean_verison = __version__[:__version__.index('+')]
else:
    clean_verison = __version__
del get_versions


def fake_decorator(arg1=0, arg2=0, arg3=0):
    def calling_function(__function):
        """
        Fake Decorator
        """
        def wrapper(*args, **kwargs):
            return __function(*args, **kwargs)
        return wrapper
    return calling_function

default_timestamp = 86400