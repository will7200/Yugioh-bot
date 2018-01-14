HIGH_CORR = 3
LOW_CORR = 2
battlemode = "NPC Battle Mode,Points: (%d,%d) at location: (%d), message: %s"
current_version = "v2"
nox_current_version = current_version
alpha_numeric = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def look_up_translation_correlation(corr):
    """
    Translates correlation to a word
    :param corr: int
    :return: str
    """
    messages = {
        str(HIGH_CORR): 'HIGH',
        str(LOW_CORR) : 'LOW'
    }
    return messages.get(str(corr), "UNKNOWN")


def tupletodict(top, left, height, width):
    """
    Converts the parameters passed in to dictionary
    :param top: int
    :param left: int
    :param height: int
    :param width: int
    :return: dict
    """
    return {
        'top'   : top,
        'left'  : left,
        'width' : width,
        'height': height
    }
