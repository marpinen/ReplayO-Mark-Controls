# -*- coding: utf-8 -*-
"""
Scales image to fit to screen, saves *_scaled.png and returns the new file name
"""
import pyautogui
import cv2
import os


sizeMult = 0.9

def scale_image_to_fit_screen(image):
    
    # Remove extension
    name = image.rsplit('.', 1)[0]
    
    # Load image
    image = cv2.imread(image)
      
    # Get screen size
    screen_width = pyautogui.size()[0]
    screen_height = pyautogui.size()[1]

    # Get image size
    height, width = image.shape[:2]

    # Calculate scale factor
    scale_factor = min(screen_width / width, screen_height / height)*sizeMult

    # Calculate new dimensions
    new_width, new_height = int(width * scale_factor), int(height * scale_factor)
    
    # Resize image
    if new_height < height:
        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
    # Define temp directory
    temp_dir = 'temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Filename
    filename = os.path.join(temp_dir, name + '_scaled' + '.png')
    
    # Saving the image
    cv2.imwrite(filename, resized_image)
    
    # Return new name
    return filename
