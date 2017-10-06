import cv2
import pickle as _pickle
import os as _os
import numpy as _np
import bot.utils as utils
from bot.shared import *
from datetime import datetime
from bot.shared import pickle_version_cache
from PIL import Image

left = 319
top = 79
width = 80
height = 23
auto_duel_box = (left, top, left + width, top + height)
autoduel = {
    'left': 319,
    'top': 79,
    'width': 80,
    'height': 23,
}
duel_variant = {
    'left': 210,
    'top': 680,
    'width': 265 - 210,
    'height': 710 - 680
}

duel_variant_v = {
    'v1':   (230, 690),
    'v2-duel': (120, 690),
    'v2-autoduel': (290, 690)
}
pickle_cache = None
last_read = datetime.now()


def read_pickle_file():
    global pickle_cache
    last_read = datetime.now()
    pickle_cache = _pickle.load(
        open(defaultlocations.cache_generation, "rb"))


def get_cache():
    global pickle_cache
    if not _os.path.exists(defaultlocations.cache_generation):
        generate()
    if pickle_cache is None:
        read_pickle_file()
        if not 'version' in pickle_cache or pickle_cache['version'] != pickle_version_cache:
            generate()
            read_pickle_file()
        return pickle_cache
    if (datetime.now() - last_read).total_seconds() < (60 * 60 * 1000):
        read_pickle_file()
        return pickle_cache
    else:
        return pickle_cache


def get_image_stats(img, left=0, top=0, width=0, height=0):
    crop_img = img[top:(top + height), left:(left + width)]
    (means, stds) = cv2.meanStdDev(crop_img)
    stats = _np.concatenate([means, stds]).flatten()
    return stats


def generate():
    save = {}
    temp_dict = generate_autoduel_stats()
    save = {**save, **temp_dict}
    temp_dict = generate_duel_button_stats()
    save = {**save, **temp_dict}
    save['version'] = pickle_version_cache
    _pickle.dump(save, open(defaultlocations.cache_generation, "wb"))


def generate_autoduel_stats():
    location = defaultlocations.assets
    autoduelon = _os.path.join(location, "auto_duel_on.png")
    autodueloff = _os.path.join(location, "auto_duel_off.png")
    a = get_image_stats(cv2.imread(autodueloff), **autoduel)
    b = get_image_stats(cv2.imread(autoduelon), **autoduel)
    save = {
        'auto_duel_off': a,
        'auto_duel_on': b
    }
    return save


def generate_duel_button_stats():
    location = defaultlocations.assets
    new_duel_variant = _os.path.join(location, "new_duel_variant.png")
    im = cv2.imread(new_duel_variant, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(im, 240, 255)
    a = get_image_stats(_np.array(edges), **duel_variant)
    save = {
        'duel_variant': a
    }
    return save
# TODO: IMPLEMENT METHOD TO DETERMINE THE ACCURACY OR THE LIKELHOOD THAT THIS IS AN AUTODUEL BUTTON


def determine_autoduel_stats(img):
    vals = get_cache()
    autodueloff = vals['auto_duel_off']
    autoduelon = vals['auto_duel_on']
    generate_duel_button_stats()
    current = get_image_stats(img, **autoduel)
    dist1 = _np.linalg.norm(current - autoduelon)
    dist2 = _np.linalg.norm(current - autodueloff)
    if dist1 < dist2:
        return True
    return False


def determine_duel_variant(img):
    vals = get_cache()
    ver_duel_variant = vals['duel_variant']
    edges = cv2.Canny(img, 240, 255)
    current = get_image_stats(edges, **duel_variant)
    dist1 = _np.linalg.norm(current - ver_duel_variant)
    if dist1 <= 5:
        return True
    return False
