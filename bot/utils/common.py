import configparser

from os.path import expanduser, join


def rotate_list(l, n):
    return l[-n:] + l[:-n]


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def default_config():
    """Make the default configuration"""
    config = configparser.ConfigParser()

    # Directories to read from
    config['locations'] = {
        'home': join(expanduser("~"), "DuelLinksBot"),
        'assets': join(expanduser("~"), "DuelLinksBot", "assets"),
        'bin': join(expanduser("~"), "DuelLinksBot", "bin"),
        'log': join(expanduser("~"), "DuelLinksBot", "log"),
        'cache_file': join(expanduser("~"), "DuelLinksBot", "assets", "predefined.h5")
    }

    # Bot config values
    config['bot'] = {
        'killNoxOnDone': True,  # kill nox when a run through is done
        'noxLocation': r'C:\Program Files (x86)\Nox\bin',  # nox location
        'startBotOnStartUp': False,  # start bot irregardless of next run time
        'runTimePersistence': 'runTimeOptions.json',  # store runtime options to this file
        'provider': 'Choose'
    }
    return config


def make_config_file(file):
    """Make the default configuration file"""
    config = default_config()
    with open(file, 'w') as f:
        config.write(f)
