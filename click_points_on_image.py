# -*- coding: utf-8 -*-
"""

Saves coordinates of mouse clicks to an image by user. 
Inputs amount of clicks by argument, ESC quits

"""

import cv2

def getCoord(image, length, msg, window_name):
    
    img = cv2.imread(image)
     
    # Draws background block and text
    height, width = img.shape[:2]
    x,y,w,h = 0,0,width,50
    cv2.rectangle(img, (x, x), (x + w, y + h), (255,255,255), -1) 
    text = msg
    coordinates = (25,30)
    font = cv2.FONT_HERSHEY_COMPLEX_SMALL
    fontScale = 0.6
    color = (0,0,0)
    thickness = 1
    img = cv2.putText(img, text, coordinates, font, fontScale, color, thickness, cv2.LINE_AA)
    
    
    # Opens windows and let the user mouse click points
    points = []
       
    def select_points(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            print(f"Selected point {x}, {y} on img")
            
       
    cv2.namedWindow(window_name)
    
    cv2.setMouseCallback(window_name, select_points)
    
    
    while True:
       if len(points) < length:
           cv2.imshow(window_name, img)
       else:
          break
       if cv2.waitKey(20) & 0xFF == 27:
           break
    

    cv2.destroyWindow(window_name)
    return points
  
