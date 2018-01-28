import configparser

from os.path import expanduser, join


def rotate_list(l, n):
    return l[-n:] + l[:-n]


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def default_config(home="."):
    """Make the default configuration"""
    config = configparser.ConfigParser()

    # Directories to read from
    config['locations'] = {
        'home'      : join(home),
        'assets'    : join(home, "assets"),
        'bin'       : join(home, "bin"),
        'log'       : join(home, "log"),
        'cache_file': join(home, "assets", "predefined.h5")
    }

    # Bot config values
    config['bot'] = {
        'startBotOnStartUp' : False,  # start bot irregardless of next run time
        'runTimePersistence': 'runTimeOptions.json',  # store runtime options to this file
        'provider'          : 'Choose',
        'sleep_factor'      : 1,
        'persist'           : True
    }

    config['steam'] = {
        'location': r'C:\Program Files (x86)\Steam'
    }

    config['nox'] = {
        'location'     : r'C:\Program Files (x86)\Nox\bin',
        'killNoxOnDone': True,  # kill nox when a run through is done
    }
    return config


def make_config_file(file):
    """Make the default configuration file"""
    config = default_config()
    with open(file, 'w') as f:
        config.write(f)
