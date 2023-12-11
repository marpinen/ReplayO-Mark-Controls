# -*- coding: utf-8 -*-
"""

Affine transforms second image to match first, by using three points on the images

"""

import cv2
import numpy as np
import time
import os

def affineT(img1, img2, points1, points2):
    
    imgStrava = cv2.imread(img1)
    imgMap = cv2.imread(img2)
  
    # convert points to numpy arrays
    pts1 = np.float32(points1)
    pts2 = np.float32(points2)
    
    # calculate the transformation matrix
    M = cv2.getAffineTransform(pts2, pts1)
    
    # apply the transformation to the second image
    height, width = imgStrava.shape[:2]
    transformed = cv2.warpAffine(src=imgMap, M=M, dsize=(width, height))
    
    # Define temp directory
    temp_dir = 'temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Filename
    filename = os.path.join(temp_dir, 'affine_output.png')
     
    # Filename
    # filename = 'affine_output.png'
      
    # Saving the image
    cv2.imwrite(filename, transformed)
    
    # display imgMap on top of imgStrava with 50% opacity
    alpha1 = 0.5
    alpha2 = 0.5
    gamma = 0
    overlay = cv2.addWeighted(imgStrava, alpha1, transformed, alpha2, gamma)
    
    time.sleep(2)
      
    cv2.imshow('Affine transform preview, press any keyboard key!', overlay)
    cv2.waitKey(0)
    
    # Close all windows
    cv2.destroyAllWindows()
    
    return filename
