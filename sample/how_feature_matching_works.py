# FROM https://docs.opencv.org/3.4/dc/dc3/tutorial_py_matcher.html

# before using this, you should install some dependencies:
#   pip install opencv-contrib-python==3.4.1.15
#   pip install matplotlib

import cv2 as cv
import matplotlib.pyplot as plt

img1 = cv.imread('pics/wechat_logo.png', cv.IMREAD_GRAYSCALE)  # queryImage
img2 = cv.imread('pics/screen.png', cv.IMREAD_GRAYSCALE)  # trainImage

# Initiate SIFT detector
sift = cv.xfeatures2d.SIFT_create()

# find the keypoints and descriptors with SIFT
kp1, des1 = sift.detectAndCompute(img1, None)
kp2, des2 = sift.detectAndCompute(img2, None)

# BFMatcher with default params
bf = cv.BFMatcher()
matches = bf.knnMatch(des1, des2, k=2)

# Apply ratio test
good = []
for m, n in matches:
    if m.distance < 0.75 * n.distance:
        good.append([m])

# get points' position in target pictures
# https://stackoverflow.com/questions/30716610/how-to-get-pixel-coordinates-from-feature-matching-in-opencv-python
point_list = list()
for each in good:
    img1_idx = each[0].queryIdx
    img2_idx = each[0].trainIdx
    point_list.append(kp2[img2_idx].pt)
print('target point: {}'.format(str(point_list)))


# cv.drawMatchesKnn expects list of lists as matches.
img3 = cv.drawMatchesKnn(img1, kp1, img2, kp2, good, None, flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
plt.imshow(img3), plt.show()
