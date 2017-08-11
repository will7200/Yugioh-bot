from os.path import expanduser, join
import os as _os
HIGH_CORR = 3
LOW_CORR = 2
battlemode = "NPC Battle Mode,Points: (%d,%d) at location: (%d), message: %s"
home_location = expanduser("~")
assets_location = join(home_location, "assets")
bin_location = join(home_location, "bin")
log_location = join(home_location, "log")

defaults_locations = {
    "home": home_location,
    "assets": assets_location,
    "bin_l": bin_location,
    "log": log_location,
    "level": "INFO",
    "killnoxondone":True
}


class locations(object):
    home = home_location
    assets = assets_location
    bin_l = bin_location
    log = log_location
    take = ["home", "assets", "bin_l", "log"]

    def __init__(self, dictionary):
        self.assign(dictionary)
        #self.makedirs()

    def assign(self, d):
        for key, value in d.items():
            if key in self.take:
                setattr(self, key, value)
            if key == "bin":
                rkey = "bin_l"
                setattr(self, rkey, value)

    def getdict(self):
        return {
            "home": self.home,
            "assets": self.assets,
            "bin": self.bin_l,
            "log": self.log,
        }

    def newRoot(self, rootpath):
        self.home = rootpath
        self.assets = join(rootpath, "assets")
        self.bin_l = join(rootpath, "bin")
        self.log = join(rootpath, "log")

    def makedirs(self):
        for folder in self.take:
            folder = getattr(self,folder)
            if not _os.path.exists(folder):
                _os.mkdir(folder)


defaultlocations = locations(defaults_locations)
