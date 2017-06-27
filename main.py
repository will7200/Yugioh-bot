import time
import os
import traceback
import datetime
import sys
import threading
import configparser
import bot.utils as utils
from logging.handlers import RotatingFileHandler
from PIL import Image, ImageOps, ImageChops
from matplotlib import pyplot as plt
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from bot.data import setDatafile, writeDatefile, readDatefile, data_object
from bot.yugioh import tapnsleep, SetupLogger, compareWithBackButton, Auto
from bot.shared import defaults_locations, home_location, defaultlocations
#sys.stdout = open(os.path.dirname(os.path.realpath(__file__))+'\\file1.txt', 'a')
Config = configparser.SafeConfigParser(defaults=defaults_locations)
Config.read("config.ini")
root_dir = Config.get("locations", "home")
if root_dir != home_location:
    defaultlocations.newRoot(root_dir)
    Config = configparser.SafeConfigParser(defaults=defaultlocations.getdict())
    Config.read("config.ini")
assets_dir = Config.get("locations", "assets")
bin_dir = Config.get("locations", "bin")
log_dir = Config.get("locations", "log")
data_file = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "run_at.json")
root = SetupLogger(log_dir, stream=True)
defaultlocations.assign({
    "home": root_dir,
    "assets": assets_dir,
    "log": log_dir,
    "bin": bin_dir,
})
setDatafile(data_file)
sched = BlockingScheduler()


# os.chdir("C:\\Users\\wf08\\OneDrive\\Yu-gi-oh_bot")

def main():
    data_object.last_run_at = datetime.datetime.now()
    writeDatefile(data_object)
    try:
        if not utils.IsNoxRunning():
            utils.StartNoxProcess("C:\\Program Files (x86)\\Nox\\bin\\Nox.exe")
            time.sleep(20)
            tapnsleep((25, 550), 10)
            tapnsleep((240, 540), 20)
        compareWithBackButton()
        Auto()
        # utils.KillNoxProcess()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(traceback.format_exc())
    utils.KillNoxProcess()
    data_object.next_run_at = datetime.datetime.now()+datetime.timedelta(hours=4)
    writeDatefile(data_object)
    sched.add_job(main, trigger='date', id='cron_main', run_date=data_object.next_run_at)
    # ScanForWord('ok')
    # runmusic()


def start():
    sched.start()


executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
    'processpool': ProcessPoolExecutor(max_workers=5)
}
sched.configure(executors=executors)
if __name__ == "__main__":
    t = threading.Thread(target=start, args=())
    t.start()
    next_run_at = readDatefile()
    if next_run_at == None:
        next_run_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
    elif datetime.datetime.now() > next_run_at:
        next_run_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
    else:
        nextAt = next_run_at - datetime.datetime.now()
        next_run_at = datetime.datetime.now(
        ) + datetime.timedelta(seconds=nextAt.total_seconds())
    sched.add_job(main, trigger='date', id='cron_main', run_date=next_run_at)
    r = input("Get Some Input")
    sched.shutdown()
    sys.exit(0)
