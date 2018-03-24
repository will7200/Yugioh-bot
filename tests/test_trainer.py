from unittest import TestCase

import os

import cv2

from bot.providers import trainer_matches as tm
from bot.shared import LOW_CORR

base = '..\\assets'


class TestTrainer(TestCase):
    def test_get_matches(self):
        location = os.path.join(base, "ok_box.png")
        base_location = os.path.join(base, "nox", "vagabond.png")
        black_screen = os.path.join(base, "nox", "black_screen.png")
        assert os.path.exists(location)
        assert os.path.exists(base_location)
        assert os.path.exists(black_screen)
        base_img = cv2.imread(base_location)
        trainer = tm.Trainer(base_img, 480, 50)
        self.assertTrue(trainer.get_matches(location, LOW_CORR) is False)
        base_img = cv2.imread(black_screen)
        trainer = tm.Trainer(base_img, 480, 50)
        self.assertTrue(trainer.get_matches(location, LOW_CORR) is False)


    def test_compare_distances(self):
        self.fail()

    def test_debug_matcher(self):
        self.fail()

    def test_read_captured_circles(self):
        self.fail()

    def test_capture_white_circles(self):
        self.fail()

    def test_draw_circles(self):
        self.fail()

    def test_prep_for_white_circles(self):
        self.fail()

    def test_compare(self):
        self.fail()

    def test_show_area(self):
        self.fail()
