import datetime
import json

import h5py
import numpy as np

from bot.utils.common import DotDict

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


"""
Pulled from:
https://codereview.stackexchange.com/questions/120802/recursively-save-python-dictionaries-to-hdf5-files-using-h5py
"""


def save_dict_to_hdf5(dic, filename, mode='w'):
    """
    ....
    """
    with h5py.File(filename, mode) as h5file:
        recursively_save_dict_contents_to_group(h5file, '/', dic)


def recursively_save_dict_contents_to_group(h5file, path, dic):
    """
    ....
    """
    for key, item in dic.items():
        if isinstance(item, (np.ndarray, np.int64, np.float64, str, bytes)):
            h5file[path + key] = item
        elif isinstance(item, dict):
            recursively_save_dict_contents_to_group(h5file, path + key + '/', item)
        else:
            raise ValueError('Cannot save %s type' % type(item))


def load_dict_from_hdf5(filename):
    """
    ....
    """
    with h5py.File(filename, 'r') as h5file:
        return recursively_load_dict_contents_from_group(h5file, '/')


def recursively_load_dict_contents_from_group(h5file, path):
    """
    ....
    """
    ans = {}
    for key, item in h5file[path].items():
        if isinstance(item, h5py._hl.dataset.Dataset):
            ans[key] = item.value
        elif isinstance(item, h5py._hl.group.Group):
            ans[key] = recursively_load_dict_contents_from_group(h5file, path + key + '/')
    return ans


if __name__ == '__main__':
    data = {'x': 'astring',
            'y': np.arange(10),
            'd': {'z': np.ones((2, 3)),
                  'b': b'bytestring'}}
    print(data)
    filename = 'test.h5'
    save_dict_to_hdf5(data, filename)
    dd = load_dict_from_hdf5(filename)
    print(dd)
