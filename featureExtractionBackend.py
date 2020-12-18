# import the necessary packages
import numpy as np
import argparse
import glob
import cv2
import imageio

import momentInvariantBackend as minv

def auto_canny(image, sigma=0.33):
    # Get median
    v = np.median(image)
    print("v",v)
    # Auto Canny edge detection median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    # return tepi
    return edged

def extract_features(im):
    if len(np.shape(im)) == 3:
        im = im[:, :, 0]
    print("IM",im)
    edge = auto_canny(im)
    feature = minv.invariant_moment(edge)
    return feature