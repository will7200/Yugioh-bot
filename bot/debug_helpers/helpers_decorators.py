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

def async_calling_function(callFrame):
    def calling_functionn(__function):
        """
        View Calling Function to debug
        """

        def wrapper(*args, **kwargs):
            cur_frame = inspect.currentframe()
            cal_frame = inspect.getouterframes(cur_frame, callFrame)
            stack = []
            for t in cal_frame:
                if 'Yu-gi' in t[1]:
                    stack.append(t[3])
            logger.debug("Called by: " + str(stack))
            return __function(*args, **kwargs)

        return wrapper
    return calling_functionn