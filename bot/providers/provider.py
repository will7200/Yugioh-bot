import asyncio
import datetime
import logging
import threading
import time
import subprocess

import apscheduler
import os

import cv2
from bot.duel_links_runtime import DuelLinkRunTime
from bot.providers import trainer_matches as tm
from bot.providers.duellinks import DuelLinks, LOW_CORR
from bot.providers.misc import Misc
from bot.providers.actions import Actions
from bot.providers.common import crop_image, mask_image


class Provider(DuelLinks, Misc, Actions):
    scheduler = None
    current_job = None  # indicates the current job running
    lock = None
    # indicates that this provider is currently battling
    current_battle = None
    # logger
    root = logging.getLogger("bot.provider")
    assets = None
    predefined = None

    def __init__(self, scheduler, config, run_time):
        self.scheduler = scheduler
        self._config = config
        self.assets = config.get('locations', 'assets')
        self.lock = None
        self.run_time = run_time  # type: DuelLinkRunTime

    def auto(self):
        t = threading.currentThread()
        self.register_thread(t)
        self.root.info("starting auto run through")
        for x in range(0, 8):
            if self.run_time.stop:
                # Leaves a checkpoint when stopped
                self.current_run = x
                break
            self.root.debug("Run through {}".format(x))
            self.compare_with_back_button()
            self.wait_for_ui(1)
            self.swipe_right()
            try:
                self.scan()
            except Exception as e:
                raise e
        self.register_thread(None)

    def debug_battle(self):
        self.battle(check_battle=self.check_battle)
        # self.CheckBattle()

    def __check_battle_is_running__(self):
        self.root.debug("CHECKING AUTO DUEL STATUS")
        img = self.get_img_from_screen_shot()
        status = self.determine_autoduel_status(img)
        self.root.debug("AUTO_DUEL STATUS: {}".format(status))
        if not status and self.current_battle:
            self.click_auto_duel()
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
        self.root.debug(job_id)

    def is_street_replay(self):
        img = self.get_img_from_screen_shot()
        street_replay = self.predefined.street_replay
        img = crop_image(img, **street_replay)
        word = self.img_to_string(img, "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
        if 'street' in word or 'replay' in word.lower():
            return True
        return False

    def get_current_page(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        area = crop_image(img, **self.predefined.page_area)
        area = mask_image([254], [255], area)
        height, width = area.shape
        current_page = 0
        for x in range(4):
            box = crop_image(area, (x * width / 4), 0, ((x + 1) * width / 4), height)
            if cv2.countNonZero(box) > 0:
                current_page = x
                break
        return current_page + 1

    def possible_battle_points(self):
        if self.run_time.stop:
            self.root.info("Received Stopping signal")
            return
        img = self.get_img_from_screen_shot()
        t = tm.Trainer(img)
        t.capture_white_circles()
        current_page = self.get_current_page(img)
        logging.debug("Current-Page {}".format(current_page))
        for x, y in t.circlePoints:
            if self.run_time.stop:
                self.root.info("Received Stopping signal")
                break
            yield x, y, current_page

    def scan(self):
        raise NotImplementedError("scan not implemented")

    def wait_for_auto_duel(self):
        self.root.debug("WAITING FOR AUTO-DUEL TO APPEAR")
        word = ''
        while 'Auto-Duel' not in word and 'AutoDuel' not in word and not self.run_time.stop:
            img = self.get_img_from_screen_shot()
            area = img.crop(self.auto_duel_box)
            try:
                word = Provider.img_to_string(area, "Auto-Duel")
            except:
                self.wait_for_ui(1)
                continue
            self.wait_for_ui(.5)
        self.click_auto_duel()

    def wait_for_white_bottom(self, tryScanning=False):
        self.root.debug("WAITING FOR WHITE BOTTOM TO APPEAR")
        img = self.get_img_from_screen_shot()
        b = self.check_if_battle(img)
        while not b and not self.run_time.stop:
            if tryScanning:
                self.scan_for_word('ok', LOW_CORR)
            img = self.get_img_from_screen_shot()
            b = self.check_if_battle(img)
            if b:
                break
            self.wait_for_ui(1)

    def wait_for_ui(self, amount):
        if not self.run_time.stop:
            super(Provider, self).wait_for_ui(amount)

    def do_system_call(self, command):
        if not self.run_time.stop:
            CREATE_NO_WINDOW = 0x08000000
            subprocess.call(command, shell=True, creationflags=CREATE_NO_WINDOW)

    @staticmethod
    def img_to_string(img, char_set=None):
        cv2.imwrite("tmp\\ocr.png", img)
        command = "bin\\tess\\tesseract.exe --tessdata-dir bin\\tess\\tessdata tmp\\ocr.png tmp\\ocr "
        if char_set is not None:
            command += "-c tessedit_char_whitelist=" + char_set + " "
        command += "-psm 7 "
        command += "> nul 2>&1"
        CREATE_NO_WINDOW = 0x08000000
        subprocess.call(command, shell=True, creationflags=CREATE_NO_WINDOW)
        # Get the largest line in txt
        with open("tmp\\ocr.txt") as f:
            content = f.read().splitlines()
        output_line = ""
        for line in content:
            line = line.strip()
            if len(line) > len(output_line):
                output_line = line
        return output_line

    def __generic_wait_for__(self, message, condition_check, fn, *args, **kwargs):
        self.root.info("Waiting for {}".format(message))
        timeout = kwargs.get('timeout', 10)

        async def wait_for(self):
            exceptions_occurred = 0
            while not self.run_time.stop:
                try:
                    condition = fn(*args, **kwargs)
                except Exception as e:
                    print(e)
                    if exceptions_occurred > 5:
                        raise Exception("Maximum exception count occurred")
                    exceptions_occurred += 1
                    await self.async_wait_for_ui(1)
                    continue
                if condition_check(condition):
                    break
                await self.async_wait_for_ui(2)

        async def main(self):
            await wait_for(self)

        loop = self.run_time._loop
        task = loop.run_until_complete(asyncio.wait_for(main(self), timeout=timeout, loop=loop))
        # loop.run_until_complete(asyncio.wait_for(main(self), timeout=timeout, loop=loop))

    def __wrapper_kmeans_result(self, trainer, location, corr, info=None):
        if trainer.get_matches(location, corr):
            x, y = trainer.kmeans.cluster_centers_[0]
            if info:
                self.root.info("NPC Battle Mode,Points: ({},{}) at location: ({}), message: {}".format(
                    info.x, info.y, info.page, info.status
                ))
            self.tap(x, y)
            return True
        return False
