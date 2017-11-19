import datetime
import inspect
import logging
import os
import sys
import threading
import time
from logging.handlers import RotatingFileHandler

import apscheduler
import cv2
import numpy as np
from PIL import Image

import bot.providers.trainer_matches as tm
import bot.utils_old as utils
from bot.providers.predefined import auto_duel_box, determine_autoduel_status, determine_duel_variant, duel_variant_v
from bot.shared import *

root = logging.getLogger('bot')


class Logger:
    def __init__(self, x, y, page, message, mode=''):
        self.x = x
        self.y = y
        self.page = page
        self.status = message
        self.set_mode(mode)

    def update_message(self, message):
        self.status = message

    def set_mode(self, mode=''):
        self.mode = mode
        if mode == 'Battle Mode' or mode == 1:
            self.format = battlemode
        elif mode != "":
            self.format = "Mode: %s, " % (mode) + "message %s"
        else:
            self.format = "Mode Unspecified, status: %s"

    def get_message(self):
        if self.mode == 'Battle Mode' or self.mode == 1:
            return self.format % (self.x, self.y, self.page, self.status)
        else:
            return self.format % (self.status)

    def writeLog(self):
        root.info(self.get_message())


def setup_logger(path, level, stream=False, includeap=False):
    "With set up the logger and stream if wanted"
    level = getattr(logging, level, logging.DEBUG)
    root.setLevel(level)
    fh = RotatingFileHandler(os.path.join(
        path, "events.log"), maxBytes=100000, backupCount=5)
    fh.setLevel(level)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    root.addHandler(fh)
    if stream:
        if includeap:
            rsched = logging.getLogger('apscheduler')
            rsched.setLevel(logging.DEBUG)
            rsched.addHandler(ch)
        root.addHandler(ch)
        #r = logging.getLogger()
        # r.setLevel(logging.DEBUG)
        # r.addHandler(ch)
    return root


class DL_Bot(object):

    scheduler = None
    current_job = None
    lock = None
    current_battle = None

    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.lock = threading.Lock()

    def auto(self, callback):
        t = threading.currentThread()
        callback(t)
        for x in range(0, 8):
            if not getattr(t, "do_run", True):
                break
            compare_with_back_button()
            time.sleep(1)
            swipe_right()
            self.scan()
        callback(None)

    def debug_battle(self):
        Battle(CheckBattle=self.check_battle)
        # self.CheckBattle()

    def __check_battle_is_running__(self):
        root.debug("CHECKING AUTO DUEL STATUS")
        img = cv2.cvtColor(
            np.array(utils.GetImgFromScreenShot()), cv2.COLOR_RGB2BGR)
        status = determine_autoduel_status(img)
        root.debug("AUTO_DUEL STATUS: {}".format(status))
        if not status and self.current_battle:
            click_auto_duel()
            self.check_battle()

    def check_battle(self, signal_done=False, delay=5):
        self.lock.acquire()
        try:
            self.scheduler.remove_job(self.current_job)
        except apscheduler.jobstores.base.JobLookupError:
            if signal_done:
                self.current_battle = False
                self.lock.release()
                return
        when = datetime.datetime.now() + datetime.timedelta(seconds=delay)
        job_id = 'cron_check_battle_at_%s' % (when.isoformat())
        self.current_job = job_id
        self.scheduler.add_job(self.__check_battle_is_running__, trigger='date',
                               id=job_id, run_date=when)
        self.lock.release()
        root.debug(job_id)

    def scan(self):
        img = utils.GetImgFromScreenShot()
        t = tm.Trainer(img)
        t.whiteCircles()
        current_page = get_current_page(img)
        for x, y in t.circlePoints:
            compare_with_back_button(log=None)
            time.sleep(1)
            tapnsleep((x, y), .5)
            img1 = utils.GetImgFromScreenShot()
            battle = check_if_battle(img1)
            time.sleep(2.5)
            if battle:
                tapnsleep((150, 400), 2.5)
                battle = verify_battle()
            if battle:
                self.current_battle = True
                root.info(battlemode % (x, y, current_page, "Starting Battle"))
                scan_for_word('ok', LOW_CORR)
                p, v = battle
                tapnsleep(p, 0)
                Battle(x, y, current_page, self.check_battle)
            else:
                time.sleep(2)
                img = utils.GetImgFromScreenShot()
                logger = Logger(
                    x, y, current_page, 'failure/BackButton', "Checking, prompts or pop ups")
                loop_scan(compare_with_back_button, **{'log': logger})
                logger.update_message("failure/closeButton")
                loop_scan(scan_for_close, **{'log': logger})
                logger.update_message("success/Gift")
                loop_scan(scan_for_word, **{'word': 'ok', 'log': logger})
                # if utils.DiffImgPercent(img, img1) > .25:
            time.sleep(2)


def loop_scan(fn, **kwargs):
    limit = 3
    doit = True
    l = 0
    while doit and l <= limit:
        l += 1
        doit = fn(**kwargs)
        time.sleep(1)


def Battle(x=0, y=0, current_page=0, CheckBattle=None, version=2):
    "The main battle mode"
    if version != 2:
        wait_for_auto_duel()
        CheckBattle()
        root.debug("WAITING FOR DUEL TO FINISH")
    wait_for('OK')
    root.info(battlemode % (x, y, current_page, "Battle Ended"))
    if version != 2:
        CheckBattle(True)
    time.sleep(.5)
    utils.Tap(230, 750)
    wait_for('NEXT', True)
    tapnsleep((230, 750), .5)
    wait_for('NEXT')
    time.sleep(.3)
    utils.Tap(230, 750)
    wait_for_white_bottom(True)
    time.sleep(.5)
    tapnsleep((230, 750), .1)
    dialog = True
    while dialog:
        dialog = check_if_battle(utils.GetImgFromScreenShot())
        if dialog:
            utils.Tap(230, 750)
    time.sleep(.5)
    scan_for_word('ok', LOW_CORR)
    time.sleep(.1)
    scan_for_word('ok', LOW_CORR)


def swipe_right():
    utils.Swipe(0, 500, 100, 500)
    time.sleep(2)


def get_current_page(img):
    left = 0
    top = 775
    width = 480
    height = 25
    box = (left, top, left + width, top + height)
    area = img.crop(box)
    #area = ImageOps.posterize(area,6)
    area = utils.OnlyPureWhite(area)
    width, height = area.size
    current_page = 0
    for x in range(4):
        box = ((x * width / 4), 0, ((x + 1) * width / 4), height)
        b = area.crop(box).convert('L')
        count = 0
        for pixel in b.getdata():
            if pixel == 0:
                count += 1
        if count > 0:
            current_page = x
        # plt.imshow(b),plt.show()
    # area.save("cropped.png")
    return current_page + 1
    #print(utils.ImgToString(area, "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"))


def tapnsleep(point, time_sleep):
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    #print('caller name:', calframe[1][3])
    x, y = point
    utils.Tap(x, y)
    time.sleep(time_sleep)


def check_if_battle(img):
    img = np.array(img)
    img = img[750:800, 0:400]
    BLUE_MIN = np.array([250, 250, 250], np.uint8)
    BLUE_MAX = np.array([255, 255, 255], np.uint8)
    amount = cv2.inRange(img, BLUE_MIN, BLUE_MAX)
    if cv2.countNonZero(amount) > (50 * 200):
        return True
    return False


def verify_battle():
    try_times = 3
    version = 0
    while True:
        try_times -= 1
        img = utils.GetImgFromScreenShot()
        img = np.array(img)
        if determine_duel_variant(img):
            pointer = duel_variant_v['v2-autoduel']
            img = img[680:710, 300:420]
            version = 2
            break
        else:
            if try_times == 0:
                pointer = duel_variant_v['v1']
                img = img[680:710, 210:265]
                version = 1

    # img = img[680:710, 90:150] new version duel
    img = Image.fromarray(img).convert('L')
    ok = utils.ImgToString(img,
                           "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz").lower()
    if version == 1:
        if ok.startswith("due") or ok == "duel":
            return (pointer, version)
    if version == 2:
        if ok.startswith("auto") or 'auto' in ok:
            return (pointer, version)
    return None


def wait_for(word, tryScanning=False):
    root.debug("WAITING FOR {} BUTTON TO APPEAR".format(word))
    ok = ''
    while ok != word:
        #root.debug("waiting for {}".format(word))
        img = utils.GetImgFromScreenShot()
        img = np.array(img)
        img = img[745:770, 210:270]
        img = Image.fromarray(img)
        try:
            if tryScanning:
                scan_for_word('ok', LOW_CORR)
            ok = utils.ImgToString(img,
                                   "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
        except:
            time.sleep(1)
            continue
        if ok == word:
            break
        time.sleep(2)


def wait_for_auto_duel():
    root.debug("WAITING FOR AUTO-DUEL TO APPEAR")
    word = ''
    while 'Auto-Duel' not in word and 'AutoDuel' not in word:
        img = utils.GetImgFromScreenShot()
        area = img.crop(auto_duel_box)
        try:
            word = utils.ImgToString(area, "Auto-Duel")
        except:
            time.sleep(1)
            continue
        time.sleep(.5)
    click_auto_duel()


def click_auto_duel():
    root.debug("AUTO-DUEL FOUND CLICKING")
    time.sleep(.1)
    utils.Tap(356, 85)


def wait_for_white_bottom(tryScanning=False):
    root.debug("WAITING FOR WHITE BOTTOM TO APPEAR")
    img = utils.GetImgFromScreenShot()
    b = check_if_battle(img)
    while not b:
        if tryScanning:
            scan_for_word('ok', LOW_CORR)
        img = utils.GetImgFromScreenShot()
        b = check_if_battle(img)
        if b:
            break
        time.sleep(1)


def compare_with_back_button(corr=HIGH_CORR, log=None):
    corrword = 'HIGH' if corr == HIGH_CORR else 'LOW'
    root.debug("LOOKING FOR BACK BUTTON, {} CORRERLATION".format(corrword))
    img = utils.GetImgFromScreenShot()
    t = tm.Trainer(img, 150, 720)
    location = defaultlocations.assets
    location = os.path.join(location, "back__.png")
    if t.getMatches(location, corr):
        x, y = t.kmeans.cluster_centers_[0]
        if log:
            log.writeLog()
        utils.Tap(x, y)
        return True
    return False


def scan_for_word(word, corr=HIGH_CORR, log=None):
    corrword = 'HIGH' if corr == HIGH_CORR else 'LOW'
    root.debug("LOOK FOR WORD '{}', {} CORRERLATION".format(word, corrword))
    img = utils.GetImgFromScreenShot()
    t = tm.Trainer(img, 480, 50)
    location = defaultlocations.assets
    location = os.path.join(location, "ok_box.png")
    if t.getMatches(location, corr):
        x, y = t.kmeans.cluster_centers_[0]
        if log:
            log.writeLog()
        utils.Tap(x, y)
        return True
    return False


def scan_for_close(corr=HIGH_CORR, log=None):
    corrword = 'HIGH' if corr == HIGH_CORR else 'LOW'
    root.debug("LOOKING FOR CLOSE BUTTON, {} CORRERLATION".format(corrword))
    img = utils.GetImgFromScreenShot()
    t = tm.Trainer(img, 480, 500)
    location = defaultlocations.assets
    location = os.path.join(location, "close.png")
    if t.getMatches(location, corr):
        x, y = t.kmeans.cluster_centers_[0]
        if log:
            log.writeLog()
        utils.Tap(x, y)
        return True
    return False


def compare_with_file(x, y, filename, corr=HIGH_CORR, log=None):
    corrword = 'HIGH' if corr == HIGH_CORR else 'LOW'
    root.debug("Compare image with asset, {} CORRERLATION".format(corrword))
    t = tm.Trainer(filename, x, y)
    location = defaultlocations.assets
    location = os.path.join(location, filename)
    if t.getMatches(location, corr):
        x, y = t.kmeans.cluster_centers_[0]
        if log:
            log.writeLog()
        utils.Tap(x, y)
