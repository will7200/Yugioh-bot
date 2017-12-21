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


def mask_image(lower_mask, upper_mask, img, apply_mask=False):
    """" Masks an image"""
    shape = np.array(img.shape).flatten()
    if len(np.array(img.shape).flatten()) == 3:
        shape_size = shape[-1]
    else:
        shape_size = 1
    assert (len(lower_mask) == shape_size)
    assert (len(upper_mask) == shape_size)
    color_min = np.array(lower_mask, np.uint8)
    color_max = np.array(upper_mask, np.uint8)
    new_img = cv2.inRange(img, color_min, color_max)
    if apply_mask:
        return cv2.bitwise_and(img, img, mask=new_img)
    return new_img


def crop_image(img, left=0, top=0, width=0, height=0):
    left, top, width, height = tuple(np.asanyarray([left, top, width, height], np.uint64).tolist())
    crop_img = img[top:(top + height), left:(left + width)].copy()
    return crop_img
