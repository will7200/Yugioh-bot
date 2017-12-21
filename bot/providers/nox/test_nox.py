import asyncio
import concurrent
import os
from concurrent.futures import ThreadPoolExecutor
from unittest import TestCase

import cv2
import matplotlib.pyplot as plt
import numpy as np
from skimage.measure import compare_ssim

from bot.providers import Nox
from bot.utils.common import default_config
from duel_links_runtime import DuelLinkRunTime
from providers.common import mask_image


def mse(imageA, imageB):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err


def compare_images(imageA, imageB, title):
    # compute the mean squared error and structural similarity
    # index for the images
    m = mse(imageA, imageB)
    s = compare_ssim(imageA, imageB, multichannel=True)

    # setup the figure
    fig = plt.figure(title)
    plt.suptitle("MSE: %.2f, SSIM: %.2f" % (m, s))

    # show first image
    ax = fig.add_subplot(1, 2, 1)
    plt.imshow(imageA, cmap=plt.cm.gray)
    plt.axis("off")

    # show the second image
    ax = fig.add_subplot(1, 2, 2)
    plt.imshow(imageB, cmap=plt.cm.gray)
    plt.axis("off")

    # show the images
    plt.show()


class TestNox(TestCase):
    provider = None
    __debug_pictures__ = False

    def setUp(self):
        os.environ['LOG_CFG'] = r'D:\Sync\OneDrive\Yu-gi-oh_bot\config.ini'
        dlRuntime = DuelLinkRunTime(default_config(r'D:\Sync\OneDrive\Yu-gi-oh_bot'), None, False)
        self.provider = Nox(None, default_config(r'D:\Sync\OneDrive\Yu-gi-oh_bot'), dlRuntime)
        self.provider.sleep_factor = 0.0
        loop = asyncio.get_event_loop()
        loop.set_default_executor(ThreadPoolExecutor(2))

    def test_provider(self):
        with self.assertRaises(AssertionError) as context:
            provider = Nox(None, default_config(r'D:\Sync\OneDrive\Fake'), None)
        self.assertTrue('Missing File' in str(context.exception))

    def test_start_process(self):
        with self.assertRaises(FileNotFoundError) as context:
            self.provider.NoxPath = 'C:\\Nox\\Not\\Here'
            self.provider.start_process()

    def test_initial_pass_through(self):
        test_function = lambda x: x is False
        self.provider.__start_app__()
        with self.assertRaises(Exception) as context:
            self.provider.__generic_wait_for__('DuelLinks Landing Page', test_function,
                                               None)
        self.assertTrue('Maximum exception count' in str(context.exception))
        self.provider.sleep_factor = 0.5
        with self.assertRaises(concurrent.futures._base.TimeoutError) as context:
            self.provider.__generic_wait_for__('DuelLinks Landing Page', test_function,
                                                 self.provider.__is_initial_screen__, timeout=5)

    def test_initial_pass_through_compare(self):
        original = cv2.imread(os.path.join(self.provider.assets, "start_screen.png"))
        against = self.provider.get_img_from_screen_shot()
        wrong = cv2.imread(os.path.join(self.provider.assets, "battle.png"))

        # convert the images to grayscale
        original = mask_image([127], [255], cv2.cvtColor(original, cv2.COLOR_BGR2GRAY), True)
        against = mask_image([127], [255], cv2.cvtColor(against, cv2.COLOR_BGR2GRAY), True)
        wrong = mask_image([127], [255], cv2.cvtColor(wrong, cv2.COLOR_BGR2GRAY), True)
        # initialize the figure
        (score, diff) = compare_ssim(original, against, full=True)
        diff = (diff * 255).astype("uint8")
        self.assertTrue(score > .90, 'If this is less then .90 the initial compare of the app will fail')
        (score, nothing) = compare_ssim(original, wrong, full=True)
        self.assertTrue(score < .90)
        if self.__debug_pictures__:
            # threshold the difference image, followed by finding contours to
            # obtain the regions of the two input images that differ
            thresh = cv2.threshold(diff, 0, 255,
                                   cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0]
            # loop over the contours
            for c in cnts:
                # compute the bounding box of the contour and then draw the
                # bounding box on both input images to represent where the two
                # images differ
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(original, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.rectangle(against, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # show the output images
            diffs = ("Original", original), ("Modified", against), ("Diff", diff), ("Thresh", thresh)
            images = ("Original", original), ("Against", against), ("Wrong", wrong)
            self.setup_compare_images(diffs)
            self.setup_compare_images(images)

    def test_is_process_running(self):
        self.fail()

    def test_kill_process(self):
        self.fail()

    def setup_compare_images(self, images, compare_against_first=False):
        i = np.asarray([isinstance(x, tuple) for x in list(images)])
        assert i.all()
        fig = plt.figure("Images")
        # loop over the images
        for (i, (name, image)) in enumerate(images):
            # show the image
            ax = fig.add_subplot(2, 2, i + 1)
            ax.set_title(name)
            plt.imshow(image, cmap=plt.cm.gray)
            plt.axis("off")

        # show the figure
        plt.show()
        if not compare_against_first:
            return
        original = images[0]
        for (i, (name, image)) in enumerate(images[1:]):
            # compare the images
            compare_images(original[1], image, "Original vs. {}".format(name))
