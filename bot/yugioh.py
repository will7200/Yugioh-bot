import time
import os
import logging
import sys
import cv2
import numpy as np
from logging.handlers import RotatingFileHandler
import inspect
from PIL import Image, ImageOps, ImageChops
import bot.utils as utils
import bot.trainer_matches as tm
from bot.shared import *
import threading
import datetime
from bot.defined import auto_duel_box, determine_autoduel_stats, determine_duel_variant, duel_variant_v
import apscheduler
root = logging.getLogger('bot')


class Logger:
    def __init__(self, x, y, page, message, mode=''):
        self.x = x
        self.y = y
        self.page = page
        self.status = message
        self.setMode(mode)

    def updateMessage(self, message):
        self.status = message

    def setMode(self, mode=''):
        self.mode = mode
        if mode == 'Battle Mode' or mode == 1:
            self.format = battlemode
        elif mode != "":
            self.format = "Mode: %s, " % (mode) + "message %s"
        else:
            self.format = "Mode Unspecified, status: %s"

    def getMessage(self):
        if self.mode == 'Battle Mode' or self.mode == 1:
            return self.format % (self.x, self.y, self.page, self.status)
        else:
            return self.format % (self.status)

    def writeLog(self):
        root.info(self.getMessage())


def SetupLogger(path, level, stream=False, includeap=False):
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

    def Auto(self, callback):
        t = threading.currentThread()
        callback(t)
        for x in range(0, 8):
            if not getattr(t, "do_run", True):
                break
            compareWithBackButton()
            time.sleep(1)
            swipeRight()
            self.Scan()
        callback(None)

    def debug_battle(self):
        Battle(CheckBattle=self.CheckBattle)
        # self.CheckBattle()

    def __check_battle_is_running__(self):
        root.debug("CHECKING AUTO DUEL STATUS")
        img = cv2.cvtColor(
            np.array(utils.GetImgFromScreenShot()), cv2.COLOR_RGB2BGR)
        status = determine_autoduel_stats(img)
        root.debug("AUTO_DUEL STATUS: {}".format(status))
        if not status and self.current_battle:
            click_auto_duel()
            self.CheckBattle()

    def CheckBattle(self, signal_done=False, delay=5):
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

    def Scan(self):
        img = utils.GetImgFromScreenShot()
        t = tm.Trainer(img)
        t.whiteCircles()
        current_page = getcurrentPage(img)
        for x, y in t.circlePoints:
            compareWithBackButton(log=None)
            time.sleep(1)
            tapnsleep((x, y), .5)
            img1 = utils.GetImgFromScreenShot()
            battle = checkIfBattle(img1)
            time.sleep(2.5)
            if battle:
                tapnsleep((150, 400), 2.5)
                battle = verifyBattle()
            if battle:
                self.current_battle = True
                root.info(battlemode % (x, y, current_page, "Starting Battle"))
                ScanForWord('ok', LOW_CORR)
                p, v = battle
                tapnsleep(p, 0)
                Battle(x, y, current_page, self.CheckBattle)
            else:
                time.sleep(2)
                img = utils.GetImgFromScreenShot()
                logger = Logger(
                    x, y, current_page, 'failure/BackButton', "Checking, prompts or pop ups")
                loopscan(compareWithBackButton, **{'log': logger})
                logger.updateMessage("failure/closeButton")
                loopscan(ScanForClose, **{'log': logger})
                logger.updateMessage("success/Gift")
                loopscan(ScanForWord, **{'word': 'ok', 'log': logger})
                # if utils.DiffImgPercent(img, img1) > .25:
            time.sleep(2)


def loopscan(fn, **kwargs):
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
        waitForAutoDuel()
        CheckBattle()
        root.debug("WAITING FOR DUEL TO FINISH")
    waitFor('OK')
    root.info(battlemode % (x, y, current_page, "Battle Ended"))
    if version != 2:
        CheckBattle(True)
    time.sleep(.5)
    utils.Tap(230, 750)
    waitFor('NEXT', True)
    tapnsleep((230, 750), .5)
    waitFor('NEXT')
    time.sleep(.3)
    utils.Tap(230, 750)
    waitForWhiteBottom(True)
    time.sleep(.5)
    tapnsleep((230, 750), .1)
    dialog = True
    while dialog:
        dialog = checkIfBattle(utils.GetImgFromScreenShot())
        if dialog:
            utils.Tap(230, 750)
    time.sleep(.5)
    ScanForWord('ok', LOW_CORR)
    time.sleep(.1)
    ScanForWord('ok', LOW_CORR)


def swipeRight():
    utils.Swipe(0, 500, 100, 500)
    time.sleep(2)


def getcurrentPage(img):
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


def checkIfBattle(img):
    img = np.array(img)
    img = img[750:800, 0:400]
    BLUE_MIN = np.array([250, 250, 250], np.uint8)
    BLUE_MAX = np.array([255, 255, 255], np.uint8)
    amount = cv2.inRange(img, BLUE_MIN, BLUE_MAX)
    if cv2.countNonZero(amount) > (50 * 200):
        return True
    return False


def verifyBattle():
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


def waitFor(word, tryScanning=False):
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
                ScanForWord('ok', LOW_CORR)
            ok = utils.ImgToString(img,
                                   "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
        except:
            time.sleep(1)
            continue
        if ok == word:
            break
        time.sleep(2)


def waitForAutoDuel():
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


def waitForWhiteBottom(tryScanning=False):
    root.debug("WAITING FOR WHITE BOTTOM TO APPEAR")
    img = utils.GetImgFromScreenShot()
    b = checkIfBattle(img)
    while not b:
        if tryScanning:
            ScanForWord('ok', LOW_CORR)
        img = utils.GetImgFromScreenShot()
        b = checkIfBattle(img)
        if b:
            break
        time.sleep(1)


def compareWithBackButton(corr=HIGH_CORR, log=None):
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


def ScanForWord(word, corr=HIGH_CORR, log=None):
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


def ScanForClose(corr=HIGH_CORR, log=None):
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


def compareWithFile(x, y, filename, corr=HIGH_CORR, log=None):
    corrword = 'HIGH' if corr == HIGH_CORR else 'LOW'
    root.debug("Compare image with asset, {} CORRERLATION".format(corrword))
    t = tm.Trainer(img, x, y)
    location = defaultlocations.assets
    location = os.path.join(location, filename)
    if t.getMatches(location, corr):
        x, y = t.kmeans.cluster_centers_[0]
        if log:
            log.writeLog()
        utils.Tap(x, y)
