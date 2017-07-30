import json
import datetime
import bot.utils as utils

data_object = {
    'next_run_at':None,
    'last_run_at':None,
    'runnow':False,
    'stop':False
}
data_object = utils.dotdict(data_object)
data_file = "run_at.json"

def setDatafile(filepath):
    data_file=filepath

def readDatefile(key=None):
    try:
        with open(data_file) as f:
            date = json.load(f, object_hook=date_hook)
    except:
        return utils.dotdict(data_object)
    if key == None:
        return utils.dotdict(date)
    if key != None and key in date:
        return date[key]
    return None

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

def date_hook(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
        except:
            pass
    return json_dict

def writeDatefile(data):
    with open(data_file, 'w') as f:
        json.dump(data, f, sort_keys=True,
        indent=4, separators=(',', ': '),default=datetime_handler)
