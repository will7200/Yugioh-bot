import asyncio
import datetime
import logging
import threading
import subprocess

import apscheduler

import cv2
from bot.duel_links_runtime import DuelLinkRunTime
from bot.providers import trainer_matches as tm
from bot.providers.duellinks import DuelLinks, LOW_CORR, DuelError, alpha_numeric, DuelLinksInfo
from bot.providers.misc import Misc
from bot.providers.actions import Actions
from bot.common import crop_image, mask_image
from bot.modes import battle_modes
from bot.modes.SpecialEvents import StreetReplay, RankedDuelsQuickStart


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
        self.battle_modes = [x(self) for x in battle_modes]
        self.check_events = [
            StreetReplay(self),
            RankedDuelsQuickStart(self)
        ]

    def auto(self):
        t = threading.currentThread()
        self.register_thread(t)
        self.root.info("starting auto run through")
        for x in range(0, 8):
            if self.run_time.stop:
                # Leaves a checkpoint when stopped
                self.current_run = x
                break
            self.root.debug("Run through {}".format(x + 1))
            self.compare_with_back_button()
            self.wait_for_ui(1)
            self.swipe_right()
            try:
                self.scan()
            except Exception as e:
                self.register_thread(None)
                raise e
        self.register_thread(None)

    def battle_mode(self, battle, version, info):
        img = self.get_img_from_screen_shot(True)
        for mode in self.battle_modes:
            if mode.check_battle(info, img):
                mode.start(battle, version, info)
                break

    def debug_battle(self):
        self.battle(check_battle=self.check_battle)
        # self.CheckBattle()

    def __check_battle_is_running__(self):
        self.root.info("CHECKING AUTO DUEL STATUS")
        img = self.get_img_from_screen_shot()
        status = self.determine_autoduel_status(img)
        self.root.info("AUTO_DUEL STATUS: {}".format(status))
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

    def guided_mode(self):
        t = threading.currentThread()
        self.register_thread(t)
        while True:
            if self.run_time.stop:
                break
            try:
                battle, version = self.verify_battle(log=False)
                if battle:
                    dl_info = DuelLinksInfo(None, None, None, "Starting Battle")
                    self.current_battle = True
                    self.root.info("Guided mode on")
                    self.scan_for_ok(LOW_CORR)
                    self.battle_mode(battle, version, dl_info)
                    self.current_battle = False
            except DuelError:
                self.wait_for_ui(1)
            except Exception as e:
                self.register_thread(None)
                raise e
        self.register_thread(None)

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

    def special_events(self, dl_info: DuelLinksInfo):
        img = self.get_img_from_screen_shot(True)
        for event in self.check_events:
            if event.event_condition(dl_info, img):
                event.event_occurred(dl_info, img)

    def scan(self):
        raise NotImplementedError("scan not implemented")

    def verify_battle(self, ori_img=None, log=True):
        if log:
            self.root.info("Verifying battle")
        if ori_img is None:
            ori_img = self.get_img_from_screen_shot()
        img = crop_image(ori_img, **self.predefined.auto_duel_location_pre)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        word = self.img_to_string(img, alpha_numeric).lower()
        if word.startswith("auto") or 'auto' in word:
            pointer = self.predefined.duel_variant_version('v2-autoduel')
            return pointer, 2
        img = crop_image(ori_img, **self.predefined.duel_location_pre)
        word = self.img_to_string(img, alpha_numeric).lower()
        if word.startswith("due") or word == "duel":
            pointer = self.predefined.duel_variant_version('v1')
            return pointer, 1
        if log:
            self.root.debug("No Auto-Duel button or Button Found")
            self.root.critical("Cannot find the auto-duel button")
        raise DuelError("Auto Duel Button failed comparison test")

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
                found = self.scan_for_ok(LOW_CORR)
                if found:
                    self.wait_for_ui(.5)
            img = self.get_img_from_screen_shot()
            b = self.check_if_battle(img)
            if b:
                break
            self.wait_for_ui(1)
        self.root.debug("White Bottom Found")

    def wait_for_ui(self, amount):
        if not self.run_time.stop:
            super(Provider, self).wait_for_ui(amount)

    def do_system_call(self, command):
        if not self.run_time.stop:
            CREATE_NO_WINDOW = 0x08000000
            subprocess.call(command, shell=True, creationflags=CREATE_NO_WINDOW)

    @staticmethod
    def img_to_string(img, char_set=None, mask_area=None):
        if mask_area is not None:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            lower, upper = mask_area[0], mask_area[1]
            img = mask_image(lower, upper, img)
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
        throwException = kwargs.get('throw', True)

        async def wait_for(self):
            exceptions_occurred = 0
            while not self.run_time.stop:
                try:
                    condition = fn(*args, **kwargs)
                except Exception:
                    if exceptions_occurred > 5:
                        if throwException:
                            raise Exception("Maximum exception count occurred waiting for {}".format(message))
                        return False
                    exceptions_occurred += 1
                    await self.async_wait_for_ui(1)
                    continue
                if condition_check(condition):
                    break
                await self.async_wait_for_ui(2)
            return True

        async def main(self):
            return await wait_for(self)

        loop = self.run_time.get_loop()
        future = asyncio.run_coroutine_threadsafe(main(self), loop)
        return future.result(timeout)

    def __wrapper_kmeans_result__(self, trainer, location, corr, info=None):
        if trainer.get_matches(location, corr):
            x, y = trainer.kmeans.cluster_centers_[0]
            if info:
                self.root.info("NPC Battle Mode,Points: ({},{}) at location: ({}), message: {}".format(
                    info.x, info.y, info.page, info.status
                ))
            self.tap(x, y)
            return True
        return False
