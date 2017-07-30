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
            self.format = "Mode: %s, " %(mode) + "message %s"
        else:
            self.format = "Mode Unspecified, status: %s"
    def getMessage(self):
        if self.mode == 'Battle Mode' or self.mode == 1:
            return self.format % (self.x, self.y, self.page, self.status)
        else:
            return self.format % (self.status)
    def writeLog(self):
        root.info(self.getMessage())


def SetupLogger(path,level,stream=False,includeap=False):
    "With set up the logger and stream if wanted"
    level = getattr(logging,level,logging.DEBUG)
    root.setLevel(level)
    fh = RotatingFileHandler(os.path.join(path, "events.log"), maxBytes=100000, backupCount=5)
    fh.setLevel(level)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
        #r.setLevel(logging.DEBUG)
        #r.addHandler(ch)
    return root

def Auto(callback):
    for x in range(0, 8):
        t = threading.currentThread()
        callback(t)
        while getattr(t, "do_run", True):
            compareWithBackButton()
            swipeRight()
            Scan()
        break
    callback(None)

def Scan():
    img = utils.GetImgFromScreenShot()
    t = tm.Trainer(img)
    t.whiteCircles()
    current_page = getcurrentPage(img)
    for x, y in t.circlePoints:
        tapnsleep((x, y), .5)
        img1 = utils.GetImgFromScreenShot()
        battle = checkIfBattle(img1)
        if battle:
            Battle(x, y, current_page)
        else:
            time.sleep(2)
            img = utils.GetImgFromScreenShot()
            logger = Logger(x, y, current_page, 'failure/BackButton', "Checking, prompts or pop ups")
            compareWithBackButton(log=logger)
            logger.updateMessage("failure/closeButton")
            ScanForClose(log=logger)
            logger.updateMessage("success/Gift")
            ScanForWord('ok', log=logger)
            #if utils.DiffImgPercent(img, img1) > .25:
        time.sleep(2)


def Battle(x,y,current_page):
    "The main battle mode"
    root.info(battlemode %(x, y, current_page, "Starting Battle"))
    time.sleep(2.5)
    tapnsleep((150, 400), 2.5)
    root.debug("LOOK FOR WORD 'OK' LOW CORRERLATION")
    ScanForWord('ok', LOW_CORR)
    #time.sleep(1)
    utils.Tap(230, 690)
    root.debug("WAITING FOR AUTODUEL BUTTON TO APPEAR")
    waitForAutoDuel()
    root.debug("WAITING FOR DUEL TO FINISH")
    waitFor('OK')
    root.info(battlemode %(x, y, current_page, "Battle Ended"))
    time.sleep(.5)
    utils.Tap(230, 750)
    root.debug("WAITING FOR NEXT BUTTON TO APPEAR")
    waitFor('NEXT',True)
    tapnsleep((230, 750), .5)
    root.debug("WAITING FOR NEXT BUTTON TO APPEAR")
    waitFor('NEXT')
    time.sleep(.3)
    utils.Tap(230, 750)
    root.debug("WAITING FOR DIALOG TO APPEAR")
    waitForWhiteBottom()
    time.sleep(.5)
    tapnsleep((230, 750), .1)
    dialog = checkIfBattle(utils.GetImgFromScreenShot())
    if dialog:
        utils.Tap(230, 750)
    root.debug("SCANNING FOR OK CORRELATIONS")
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
    box = (left, top, left+width, top+height)
    area = img.crop(box)
    #area = ImageOps.posterize(area,6)
    area = utils.OnlyPureWhite(area)
    width, height = area.size
    current_page = 0
    for x in range(4):
        box = ((x*width/4),0,((x+1)*width/4),height)
        b = area.crop(box).convert('L')
        count = 0
        for pixel in b.getdata():
            if pixel == 0:
                count += 1
        if count > 0:
            current_page = x
        #plt.imshow(b),plt.show()
    #area.save("cropped.png")
    return current_page+1
    #print(utils.ImgToString(area, "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"))

def tapnsleep(point,time_sleep):
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    print('caller name:', calframe[1][3])
    x , y = point
    utils.Tap(x,y)
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

def waitFor(word,tryScanning=False):
    ok = ''
    while ok != word:
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
    left = 319
    top = 79
    width = 80
    height = 23
    box = (left, top, left+width, top+height)
    word = ''
    while 'Auto-Duel' not in word and 'AutoDuel' not in word:
        img = utils.GetImgFromScreenShot()
        area = img.crop(box)
        try:
            word = utils.ImgToString(area, "Auto-Duel")
        except:
            time.sleep(1)
            continue
        time.sleep(.5)
    root.debug("AUTO-DUEL FOUND CLICKING")
    time.sleep(.1)
    utils.Tap(356, 85)

def waitForWhiteBottom():
    img = utils.GetImgFromScreenShot()
    b = checkIfBattle(img)
    while not b:
        img = utils.GetImgFromScreenShot()
        b = checkIfBattle(img)
        if b:
            break
        time.sleep(1)

def compareWithBackButton(corr=HIGH_CORR, log=None):
    img = utils.GetImgFromScreenShot()
    t = tm.Trainer(img, 150, 720)
    location = defaultlocations.assets
    location = os.path.join(location, "back__.png")
    if t.getMatches(location, corr):
        x, y = t.kmeans.cluster_centers_[0]
        if log:
            log.writeLog()
        utils.Tap(x, y)

def ScanForWord(word, corr=HIGH_CORR, log=None):
    img = utils.GetImgFromScreenShot()
    t = tm.Trainer(img, 480, 0)
    location = defaultlocations.assets
    location = os.path.join(location, "ok_box.png")
    if t.getMatches(location, corr):
        x, y = t.kmeans.cluster_centers_[0]
        if log:
            log.writeLog()
        utils.Tap(x, y)
def ScanForClose(corr=HIGH_CORR, log=None):
    img = utils.GetImgFromScreenShot()
    t = tm.Trainer(img, 480, 500)
    location = defaultlocations.assets
    location = os.path.join(location, "close.png")
    if t.getMatches(location, corr):
        x, y = t.kmeans.cluster_centers_[0]
        if log:
            log.writeLog()
        utils.Tap(x, y)

def compareWithFile(x,y,filename,corr=HIGH_CORR,log=None):
    t = tm.Trainer(img, x, y)
    location = defaultlocations.assets
    location = os.path.join(location, filename)
    if t.getMatches(location, corr):
        x, y = t.kmeans.cluster_centers_[0]
        if log:
            log.writeLog()
        utils.Tap(x, y)
    
