from .provider import Provider
from bot.providers.nox import Nox
from .steam import Steam
import logging

available_providers = [Nox, Steam]


def get_provider(name):
    if name.lower() == 'nox':
        return Nox
    elif name.lower == 'steam':
        return Steam
    else:
        raise Exception("Provider {} does not exist, choose from [{}]".format(name, ','.join(
            [x.__str__() for x in available_providers])))


root = logging.getLogger("bot.providers")
root.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
root.addHandler(ch)
