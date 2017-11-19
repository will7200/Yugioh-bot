import inspect
import logging

logger = logging.getLogger("bot.debug_helpers")


def calling_function(__function):
    """
    View Calling Function to debug
    """

    def wrapper(*args, **kwargs):
        cur_frame = inspect.currentframe()
        cal_frame = inspect.getouterframes(cur_frame, 2)
        logger.debug("Called by: " + str(cal_frame[1][3]))
        return __function(*args, **kwargs)

    return wrapper
