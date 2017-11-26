import time

import cv2
import numpy as np


def loop_scan(fn, **kwargs):
    limit = 3
    doit = True
    l_times = 0
    while doit and l_times <= limit:
        l_times += 1
        doit = fn(**kwargs)
        time.sleep(1)


def mask_image(lower_mask, upper_mask, img):
    """" Masks an image"""
    assert (len(lower_mask) == 3)
    assert (len(upper_mask) == 3)
    color_min = np.array(lower_mask, np.uint8)
    color_max = np.array(upper_mask, np.uint8)
    new_img = cv2.inRange(img, color_min, color_max)
    return new_img


def crop_image(img, left=0, top=0, width=0, height=0):
    left, top, width, height = tuple(np.asanyarray([left, top, width, height], np.uint64).tolist())
    crop_img = img[top:(top + height), left:(left + width)].copy()
    return crop_img
