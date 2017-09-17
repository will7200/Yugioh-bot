import cv2
import pickle as _pickle
import os as _os
import numpy as _np
import bot.utils as utils
from bot.shared import *
left = 319
top = 79
width = 80
height = 23
auto_duel_box = (left, top, left+width, top+height)
autoduel = {
    'left':319,
    'top': 79,
    'width': 80,
    'height': 23,
}
def get_image_stats(img, left=0, top=0, width=0, height=0):
    crop_img = img[top:(top + height), left:(left + width)]
    (means, stds) = cv2.meanStdDev(crop_img)
    stats = _np.concatenate([means, stds]).flatten()
    return stats
def generate():
    location = defaultlocations.assets
    autoduelon = _os.path.join(location, "auto_duel_on.png")
    autodueloff = _os.path.join(location, "auto_duel_off.png")
    a=get_image_stats(cv2.imread(autodueloff),**autoduel)
    b=get_image_stats(cv2.imread(autoduelon),**autoduel)
    save = {
        'auto_duel_off':a,
        'auto_duel_on':b
    }
    _pickle.dump(save,open(defaultlocations.cache_generation,"wb"))

## TODO: IMPLEMENT METHOD TO DETERMINE THE ACCURACY OR THE LIKELHOOD THAT THIS IS AN AUTODUEL BUTTON
def determine_autoduel_stats(img):
    if not _os.path.exists(defaultlocations.cache_generation):
        generate()
    vals = _pickle.load(open(defaultlocations.cache_generation,"rb"))
    autodueloff = vals['auto_duel_off']
    autoduelon = vals['auto_duel_on']
    current = get_image_stats(img,**autoduel)
    dist1 = _np.linalg.norm(current-autoduelon)
    dist2 = _np.linalg.norm(current-autodueloff)
    if dist1 < dist2:
        return True
    else:
        return False