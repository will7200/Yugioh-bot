from abc import abstractmethod

import numpy as np
import cv2
import time


class Actions(object):
    """ Defines Actions that must be implemented for each Provider"""
    last_img = None

    def __init__(self):
        pass

    @abstractmethod
    def tap(self, x, y):
        raise NotImplementedError("tap not defined")

    @abstractmethod
    def swipe(self, x1, y1, x2, y2):
        raise NotImplementedError("swipe not defined")

    @abstractmethod
    def swipe_time(self, x1, y1, x2, y2, time_amount):
        raise NotImplementedError("swipe time not defined")

    @abstractmethod
    def key_escape(self):
        """Optional Key Escape"""
        raise NotImplementedError("key_escape not defined")

    @abstractmethod
    def take_png_screenshot(self):
        raise NotImplementedError("take_png_screenshot not defined")

    def get_img_from_screen_shot(self, last_one=False, fail=0):
        if last_one and self.last_img is not None:
            return self.last_img
        screen_shot = self.take_png_screenshot()
        nparr = np.fromstring(screen_shot, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if fail == 5:
            raise Exception("Cannot obtain proper image for provider")
        if img is None:
            return self.get_img_from_screen_shot(fail=fail+1)
        self.last_img = img
        return img

    @abstractmethod
    def swipe_right(self, time_sleep=0):
        raise NotImplementedError("swipe right not defined")

    def tapnsleep(self, point, time_sleep, relative=False):
        x, y = point
        self.tap(x, y)
        self.wait_for_ui(time_sleep)

    @abstractmethod
    def wait_for_ui(self, time_sleep):
        raise NotImplementedError("wait_for_ui not defined")
