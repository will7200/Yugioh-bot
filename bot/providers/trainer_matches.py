import numpy as np
import cv2
from matplotlib import pyplot as plt
import os

from bot.common import mask_image

os.environ['FOR_DISABLE_CONSOLE_CTRL_HANDLER'] = 'T'
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import euclidean_distances


class Trainer(object):
    _debug = False

    def __init__(self, query, x=0, y=0):
        self.query = query
        self.xThreshold = x
        self.yThreshold = y
        if type(query) is np.ndarray:
            self.query = query
        else:
            self.query = cv2.imread(query, 0)
        self.goodMatches = []
        self.images = []
        self.circlePoints = []
        self.kmeans = None
        self.white_query = None

    def get_matches(self, train, corr):
        train_img = cv2.imread(train, 0)
        query_img = self.query
        # Initiate SIFT detector
        sift = cv2.xfeatures2d.SIFT_create()

        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(train_img, None)
        kp2, des2 = sift.detectAndCompute(query_img, None)
        if des1 is None or des2 is None:
            return False
        # create BFMatcher object
        bf = cv2.BFMatcher()
        try:
            matches = bf.knnMatch(des1, des2, k=2)
        except cv2.error:
            return False
        good_matches = []
        cluster = []
        for m, n in matches:
            img2_idx = m.trainIdx
            img1_idx = m.queryIdx
            (x1, y1) = kp1[img1_idx].pt
            (x2, y2) = kp2[img2_idx].pt
            # print("Comare %d to %d and %d to %d" % (x1,x2,y1,y2))
            if m.distance < 0.8 * n.distance and y2 > self.yThreshold and x2 < self.xThreshold:
                good_matches.append([m])
                cluster.append([int(x2), int(y2)])
        if len(cluster) <= corr:
            return False
        self.kmeans = KMeans(n_clusters=1, random_state=0).fit(cluster)
        new_cluster, new_matches = self.compare_distances(train_img, cluster, good_matches)
        if len(new_cluster) == 0 or len(new_cluster) / len(cluster) < .5:
            return False
        img3 = cv2.drawMatchesKnn(
            train_img, kp1, query_img, kp2, new_matches, None, flags=2)
        if self._debug:
            self.images.append(img3)
            self.debug_matcher(img3)
        return True

    def compare_distances(self, train_img, cluster, good_matches):
        # sometimes the sift algorithm matches random points on screen so therefore
        # it is necessary to determine the euclidean distances between these points
        distances = euclidean_distances([self.kmeans.cluster_centers_[0]], cluster)
        height, width = train_img.shape
        new_cluster = []
        new_matches = []
        # If all the points are greater than np.sqrt((width / 2) ** 2 + (height / 2) ** 2)
        # Which then we can assume that they are not correct
        # this will only work on images that fit the same dimensions against the query image
        for index, distance in enumerate(distances[0]):
            if distance <= np.sqrt((width / 2) ** 2 + (height / 2) ** 2):
                new_cluster.append(cluster[index])
                new_matches.append(good_matches[index])
        return new_cluster, new_matches

    def debug_matcher(self, img):
        # plt.scatter(*zip(*cluster)),plt.axis([0,480,0,800]),plt.gca().invert_yaxis(),plt.show()
        # plt.imshow(img)
        # plt.show()
        cv2.imwrite('debug_pic.png', img)

    def read_captured_circles(self):
        img = cv2.cvtColor(self.query, cv2.COLOR_BGR2GRAY)
        img = cv2.medianBlur(img, 7)
        cimg = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 30,
                                   param1=50, param2=30, minRadius=20, maxRadius=50)
        if circles is None:
            return
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            if i[1] < 400:
                continue
            self.circlePoints.append((i[0], i[1]))
        if self._debug:
            self.draw_circles(circles, cimg)

    def capture_white_circles(self, x_limit=480, y_limit=670):
        self.prep_for_white_circles()
        img = cv2.cvtColor(self.white_query, cv2.COLOR_BGR2GRAY)
        cimg = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 40,
                                   param1=50, param2=30, minRadius=5, maxRadius=60)
        if circles is None:
            return
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            if i[0] <= x_limit and i[1] <= y_limit:
                self.circlePoints.append((i[0], i[1]))
        if self._debug:
            self.draw_circles(circles, cimg)

    def draw_circles(self, circles, cimg):
        for i in circles[0, :]:
            # draw the outer circle
            cv2.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)
        self.images.append(cimg)

    def prep_for_white_circles(self):
        lower, upper = ([215, 215, 215], [255, 255, 255])
        self.white_query = mask_image(lower, upper, self.query, apply_mask=True)

    def compare(self):
        if len(self.images) > 0:
            plot_image = self.images[0]
            for x in range(1, len(self.images)):
                plot_image = np.concatenate((plot_image, self.images[x]), axis=1)
            plt.imshow(plot_image), plt.show()

    @staticmethod
    def show_area(x, y, image):
        if type(image) is np.ndarray:
            pass
        else:
            image = cv2.imread(image)
        h, w, d = image.shape
        image = image[0:max(0, (h - y) - 1), 0:max(x, 0)]
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)), plt.show()


class BoundingTrainer(Trainer):

    def __init__(self, query, x=0, y=0, w=0, h=0, bounding_area=None, blacklist=None):
        if bounding_area is not None:
            x, y, w, h = bounding_area.get('left'), bounding_area.get('top'), \
                         bounding_area.get('width'), bounding_area.get('height')
        super(BoundingTrainer, self).__init__(query, x, y)
        self.xThreshold_lower = self.xThreshold
        self.yThreshold_lower = self.xThreshold
        self.blacklist = None
        if w is None:
            self.xThreshold_upper = self.query.shape[1]
        else:
            self.xThreshold_upper = x + w
        if h is None:
            self.yThreshold_upper = self.query.shape[0]
        else:
            self.yThreshold_upper = y + h

    def in_box(self, x, y):
        if self.xThreshold_lower <= x <= self.xThreshold_upper:
            if self.yThreshold_lower <= y <= self.yThreshold_upper:
                return True
        return False

    def in_blacklist(self, x, y):
        if self.blacklist:
            for exclude in self.blacklist:
                cx, cy, cw, ch = exclude.get('left'), exclude.get('top'), \
                                 exclude.get('width'), exclude.get('height')
                if cx <= x <= cx + cw:
                    if cx <= y <= cy + ch:
                        return True
            return False

    def get_matches(self, train, corr):
        train_img = cv2.imread(train, 0)
        query_img = self.query
        # Initiate SIFT detector
        sift = cv2.xfeatures2d.SIFT_create()

        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(train_img, None)
        kp2, des2 = sift.detectAndCompute(query_img, None)
        if des1 is None or des2 is None:
            return False
        # create BFMatcher object
        bf = cv2.BFMatcher()
        try:
            matches = bf.knnMatch(des1, des2, k=2)
        except cv2.error:
            return False
        good_matches = []
        cluster = []
        for m, n in matches:
            img2_idx = m.trainIdx
            img1_idx = m.queryIdx
            (x1, y1) = kp1[img1_idx].pt
            (x2, y2) = kp2[img2_idx].pt
            # print("Comare %d to %d and %d to %d" % (x1,x2,y1,y2))
            if m.distance < 0.8 * n.distance and self.in_box(x2, y2):
                good_matches.append([m])
                cluster.append([int(x2), int(y2)])
        if len(cluster) <= corr:
            return False
        self.kmeans = KMeans(n_clusters=1, random_state=0).fit(cluster)
        new_cluster, new_matches = self.compare_distances(train_img, cluster, good_matches)
        if len(new_cluster) == 0 or len(new_cluster) / len(cluster) < .5:
            return False
        img3 = cv2.drawMatchesKnn(
            train_img, kp1, query_img, kp2, new_matches, None, flags=2)
        if self._debug:
            self.images.append(img3)
            self.debug_matcher(img3)
        return True

    def capture_white_circles(self):
        self.prep_for_white_circles()
        img = cv2.cvtColor(self.white_query, cv2.COLOR_BGR2GRAY)
        img = cv2.medianBlur(img, 1)
        cimg = cv2.cvtColor(self.query, cv2.COLOR_BGR2RGB)
        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, img.shape[0] / 15,
                                   param1=50, param2=22, minRadius=5, maxRadius=60)
        if circles is None:
            return
        circles = np.uint16(np.around(circles))
        new_circles = []
        for i in circles[0, :]:
            if self.in_box(i[0], i[1]) and not self.in_blacklist(i[0], i[1]):
                self.circlePoints.append((i[0], i[1]))
                new_circles.append(i)
        if self._debug:
            # self.draw_circles(circles, cimg)
            if len(new_circles) > 0:
                self.draw_circles(np.array([new_circles]), cimg)

    @staticmethod
    def show_area(x, y, w, h, image):
        if type(image) is np.ndarray:
            pass
        else:
            image = cv2.imread(image)
        if h is None:
            h = image.shape[0]
        if w is None:
            w = image.shape[1]
        image = image[y:y + h, x:x + w]
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)), plt.show()

    @staticmethod
    def show_area_bounded(bounding_area, image):
        return BoundingTrainer.show_area(bounding_area.get('left'),
                                         bounding_area.get('top'),
                                         bounding_area.get('width'),
                                         bounding_area.get('height'),
                                         image)
