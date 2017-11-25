import json
import datetime
from bot.utils.common import DotDict
import os as _os

data_object = {
    'next_run_at': None,
    'last_run_at': None,
    'runnow': False,
    'stop': False
}
data_object = DotDict(data_object)
data_file_name = "run_at.json"
data_file = data_file_name


def set_data_file(file_path):
    global data_file
    data_file = file_path


def read_data_file(key=None):
    try:
        with open(data_file) as f:
            data = json.load(f, object_hook=date_hook)
            data = DotDict(data)
    except:
        data = DotDict(data_object)
    if key == None:
        return data
    if key != None and key in data:
        return data[key]
    return None


def read_json_file(file=data_file):
    try:
        with open(file) as f:
            data = json.load(f, object_hook=date_hook)
            return data
    except FileNotFoundError:
        return None


def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    print(x, type(x))
    raise TypeError("Unknown type")


try_formats = ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"]


def date_hook(json_dict):
    for (key, value) in json_dict.items():
        for try_format in try_formats:
            try:
                json_dict[key] = datetime.datetime.strptime(
                    value, try_format)
            except:
                pass
    return json_dict


def write_data_file(data, file=data_file):
    with open(file, 'w') as f:
        json.dump(data, f, sort_keys=True,
                  indent=4, separators=(',', ': '), default=datetime_handler)
