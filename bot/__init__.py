import logging
from bot.debug_helpers.logger import LastRecordHandler
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
last_record = LastRecordHandler()
logger.addHandler(ch)
logger.addHandler(last_record)
logger.debug("Setup Complete")
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
