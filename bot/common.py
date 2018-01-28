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
    """" Masks an image according to the upper and lower bounds
    Parameters
    ----------
    lower_mask : ndarray
        lower mask to apply to image, length must match image channels
    upper_mask : ndarray
        upper mask to apply to image, length must match image channels
    img :  ndarray
        image to apply mask to
    apply_mask : bool
        returns the masked image instead of the mask itself
    """
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


def mse(image_a, image_b):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((image_a.astype("float") - image_b.astype("float")) ** 2)
    err /= float(image_a.shape[0] * image_a.shape[1])

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err


def crop_image(img, left=0, top=0, width=0, height=0):
    left, top, width, height = tuple(np.asanyarray([left, top, width, height], np.uint64).tolist())
    crop_img = img[top:(top + height), left:(left + width)].copy()
    return crop_img


def bot_assertion(condition, error_type, message):
    if not condition:
        raise error_type(message)


def first_true(iterable, default=False, pred=None):
    """Returns the first true value in the iterable.

    If no true value is found, returns *default*

    If *pred* is not None, returns the first item
    for which pred(item) is true.

    """
    # first_true([a,b,c], x) --> a or b or c or x
    # first_true([a,b], x, f) --> a if f(a) else b if f(b) else x
    return next(filter(pred, iterable), default)
