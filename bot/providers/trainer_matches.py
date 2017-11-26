import numpy as np
import cv2
from matplotlib import pyplot as plt
import PIL as Pillow
import os
os.environ['FOR_DISABLE_CONSOLE_CTRL_HANDLER'] = 'T'
from sklearn.cluster import KMeans


class Trainer(object):
    def __init__(self, query, x=0, y=0):
        self.query = query
        self.xThreshold = x
        self.yThreshold = y
        if type(query) is Pillow.Image.Image:
            self.query = cv2.cvtColor(np.array(self.query), cv2.COLOR_RGB2BGR)
        elif type(query) is np.ndarray:
            self.query = query
        else:
            self.query = cv2.imread(query, 0)
        self.goodMatches = []
        self.images = []
        self.circlePoints = []
        self.kmeans = None
        self.whitequery = None

    def getMatches(self, train, corr):
        img1 = cv2.imread(train, 0)  # trainImage
        img2 = self.query  # queryImage
        # Initiate SIFT detector
        sift = cv2.xfeatures2d.SIFT_create()

        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(img1, None)
        kp2, des2 = sift.detectAndCompute(img2, None)

        # create BFMatcher object
        bf = cv2.BFMatcher()
        try:
            matches = bf.knnMatch(des1, des2, k=2)
        except cv2.error:
            return False
        goodMatches = []
        cluster = []
        for m, n in matches:
            img2_idx = m.trainIdx
            img1_idx = m.queryIdx
            (x1, y1) = kp1[img1_idx].pt
            (x2, y2) = kp2[img2_idx].pt
            #print("Comare %d to %d and %d to %d" % (x1,x2,y1,y2))
            if m.distance < 0.8 * n.distance and y2 > self.yThreshold and x2 < self.xThreshold:
                goodMatches.append([m])
                cluster.append([int(x2), int(y2)])
        if len(cluster) <= corr:
            return False
        self.kmeans = KMeans(n_clusters=1, random_state=0).fit(cluster)
        # print(self.kmeans.cluster_centers_)
        # plt.scatter(*zip(*cluster)),plt.axis([0,480,0,800]),plt.gca().invert_yaxis(),plt.show()
        img3 = cv2.drawMatchesKnn(
            img1, kp1, img2, kp2, goodMatches, None, flags=2)
        self.images.append(img3)
        # if train != 'assets/back__.png':
        #plt.imshow(img3),plt.show()
        return True
        # return goodMatches
        # cv2.drawMatchesKnn expects list of lists as matches.

    def readCircles(self):
        img = cv2.cvtColor(self.query, cv2.COLOR_BGR2GRAY)
        img = cv2.medianBlur(img, 7)
        cimg = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 30,
                                   param1=50, param2=30, minRadius=20, maxRadius=50)
        if circles is None:
            return
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            # draw the outer circle
            if (i[1] < 400):
                continue
            self.circlePoints.append((i[0], i[1]))
            cv2.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)
        # plt.imshow(cimg),plt.show()
        self.images.append(cimg)

    def whiteCircles(self):
        self.prepForWhiteCircles()
        img = cv2.cvtColor(self.whitequery, cv2.COLOR_BGR2GRAY)
        cimg = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 40,
                                   param1=50, param2=30, minRadius=5, maxRadius=60)
        if circles is None:
            return
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            self.circlePoints.append((i[0], i[1]))
            # draw the outer circle
            cv2.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)
        #cv2.imshow("images", np.hstack([cimg]))
        # cv2.waitKey(0)

    def prepForWhiteCircles(self):
        lower, upper = ([215, 215, 215], [255, 255, 255])
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")

        # find the colors within the specified boundaries and apply
        # the mask
        mask = cv2.inRange(self.query, lower, upper)
        output = cv2.bitwise_and(
            self.query, self.query, mask=mask)  # coding=utf-8
        self.whitequery = output

    def compare(self):
        plot_image = self.images[0]
        for x in range(1, len(self.images)):
            plot_image = np.concatenate((plot_image, self.images[x]), axis=1)
        plt.imshow(plot_image), plt.show()
