# -*- coding: utf-8 -*-
"""
ReplayO: Mark Controls

Helper program to mark orienteering control points to map and view them 
with Strava activity.

WINDOWS ONLY, NOT TESTED WITH OTHER OS!

Prerequisites:
You need a Strava account, at least one activity and these API keys: 
https://developers.strava.com/docs/getting-started/#account

Add your Strava API keys to strava_api_keys/strava_api_keys.txt -file!


How to use:
1. Go orienteering! Start your GPS tracker at the start and stop it at the finish. 
   Remember to take a photo of your paper orienteering map!
2. Crop the photo so that start, finish and all control points are visible.
   Include some good map feature points, like roads and other human made stuff. We will need three
   feature points that are as far of each other as possible for the map alignment.
3. Run the program, select the map photo and paste your Strava activitys URL, and click GO.
4. Click three same map feature points from both maps. You may need to do this several times to get
   a good result.
5. Press ESC-key to exit the preview window
6. Click first the start, then all the controls in right order, and last the finish. 
   When you are done, hit ESC.
7. Your track with control points opens in a browser window, or manually open output/final_map.html file.

WIP: 
- GPX file input 
- OAuth
- A lot of improvements and fixes
- A web app to replay animated Strava activity and compare with friends activity.

"""

import numpy as np
import folium
from geopy.distance import geodesic
from html2image import Html2Image
import subprocess
import webbrowser
from strava_fetch_process import fetchStrava
from affine_transform import affineT
from scale_img_to_screen import scale_image_to_fit_screen as scaleFit
from click_points_on_image import getCoord
import os
from folium.features import DivIcon
import threading
import time
from queue import Queue
import json
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox


def pixel_to_coord(x, y, img_width, img_height, ne_coord, sw_coord):
    
    # Calculate the width and height of the image in meters
    img_width_m = geodesic(ne_coord, (ne_coord[0], sw_coord[1])).m
    img_height_m = geodesic(ne_coord, (sw_coord[0], ne_coord[1])).m

    # Calculate the width and height of a single pixel in meters
    pixel_width_m = img_width_m / img_width
    pixel_height_m = img_height_m / img_height

    # Calculate the distance from the top left corner of the image to the target pixel
    x_dist_m = x * pixel_width_m
    y_dist_m = y * pixel_height_m

    # Calculate the new coordinate by moving from the top left corner of the image to the target pixel
    new_coord = geodesic(meters=y_dist_m).destination(geodesic(meters=x_dist_m).destination(ne_coord, 90), 180)

    return new_coord

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.geometry("250x250")
        self.master.title("ReplayO: Mark Controls")
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        
        '''
        # GPX button for future support
        self.gpx_button = tk.Button(self)
        self.gpx_button["text"] = "GPX file"
        self.gpx_button["command"] = self.load_gpx
        self.gpx_button.pack(side="top")
        '''
    
        btext_pad = 10
        button_pad = 5

        self.strava_button = tk.Button(self, text="Strava URL", command=self.load_strava, padx=btext_pad, pady=btext_pad)
        self.strava_button.pack(side="top", pady=button_pad)
        
        self.map_button = tk.Button(self, text="Map image", command=self.load_map, padx=btext_pad, pady=btext_pad)
        self.map_button.pack(side="top", pady=button_pad)
        
        self.ok_button = tk.Button(self, text="GO", command=self.check_inputs, padx=btext_pad, pady=btext_pad)
        self.ok_button.pack(side="top", pady=button_pad)
        
        self.quit_button = tk.Button(self, text="Quit", command=self.master.destroy, padx=btext_pad, pady=btext_pad)
        self.quit_button.pack(side="top", pady=button_pad)


    def load_gpx(self):
        self.gpx_file = filedialog.askopenfilename()
        print(f"You selected a GPX file: {self.gpx_file}")
        if hasattr(self, 'strava_url'):
            delattr(self, 'strava_url')

    def load_strava(self):
        self.strava_url = simpledialog.askstring("Input", "URL to your Strava activity:")
        print(f"You entered a Strava URL: {self.strava_url}")
        if hasattr(self, 'gpx_file'):
            delattr(self, 'gpx_file')
            
        # Check does the strava_api_keys.txt exists and has values
        stravaAPIfile = 'strava_api_keys/strava_api_keys.txt'
    
        if os.path.isfile(stravaAPIfile):
            with open(stravaAPIfile, 'r') as file:
                lines = file.readlines()
    
            client_id = lines[0].split('=')[1].strip().replace("'", "")
            client_secret = lines[1].split('=')[1].strip().replace("'", "")
            refresh_token = lines[2].split('=')[1].strip().replace("'", "")
    
            # Check if client_id has values
            if client_id:
                print("client_id has a value.")
                self.activity = fetchStrava(self.strava_url, client_id, client_secret, refresh_token)
                
                if self.activity is None:
                    messagebox.showerror("Error", "Error fetching Strava activity")
                    delattr(self, 'strava_url')
                    
                
            else:
                messagebox.showerror("Error", "strava_api_keys.txt does not have values")
                delattr(self, 'strava_url')
        else:
            messagebox.showerror("Error", "strava_api_keys.txt does not exist")
            delattr(self, 'strava_url')
            
            
    def load_map(self):
        self.imgMap = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        print(f"You selected a map image: {self.imgMap}")


    def check_inputs(self):
        if hasattr(self, 'imgMap') and (hasattr(self, 'gpx_file') or hasattr(self, 'strava_url')):
            print("All necessary inputs have been provided.")
            # Add your code here to handle the inputs
            if hasattr(self, 'gpx_file'):
                # GPX file operations
                # print('Do gps things')
                self.continue_program(self.activity, self.imgMap)
            else:
                # Strava operations
                # print('Do Strava things')
                self.continue_program(self.activity, self.imgMap)
                
        else:
            messagebox.showerror("Error", "Please provide both Strava URL and Map image file")


    def continue_program(self, activity, imgMap):
        print("Continuing the program succesfully")
        
        # plot activity on map
        m = folium.Map(zoomSnap=0.001, zoomControl=False,
                       attributionControl=False)

        folium.PolyLine(activity['map.polyline'], color='red', weight=2).add_to(m)

        # Custom padding around activity in coords
        customPad = 0.002

        # fit bounds
        sw = [
            (np.min([coord[0] for coord in activity['map.polyline']])) - customPad,
            (np.max([coord[1] for coord in activity['map.polyline']])) + customPad
        ]

        ne = [
            (np.max([coord[0] for coord in activity['map.polyline']])) + customPad,
            (np.min([coord[1] for coord in activity['map.polyline']])) - customPad
        ]


        # https://python-visualization.github.io/folium/modules.html
        bound_pad = (0, 0)  # zoomSnap needs to be set < 1
        m.fit_bounds([sw, ne], padding=bound_pad)
        
        
        # Define temp directory
        temp_dir = 'temp'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)


        # display(m)
        m.save(os.path.join(temp_dir, 'imgStrava.html'))


        # get px size from bounding box coordinates
        sizeReduce = 0.65  # to fit to the screen
        bottom_left = (sw[0], sw[1])
        top_right = (ne[0], ne[1])
        width = int(geodesic(bottom_left, (bottom_left[0], top_right[1])).meters*sizeReduce)
        height = int(geodesic(bottom_left, (top_right[0], bottom_left[1])).meters*sizeReduce)
        
        
        # html to image
        hti = Html2Image(
            custom_flags=['--virtual-time-budget=10000', '--hide-scrollbars'],
            # output_path=temp_dir
        )
        
        hti.output_path = temp_dir
        
        hti.screenshot(
            html_file='temp\imgStrava.html',
            size=(width, height),
            save_as='imgStrava.png'
        )
        
        imgStrava = os.path.join(temp_dir, 'imgStrava.png')
        
        
        # Delete temp html file
        os.remove(os.path.join(temp_dir, "imgStrava.html"))


        # Scale image to fit screen
        scaled_imgMap = scaleFit(imgMap)


        # Open magnifier
        magnify = subprocess.Popen(['python', 'screen_magnifier.py'])


        def threaded_getCoord(q, *args):
            result = getCoord(*args)
            q.put(result)

        q1 = Queue()
        q2 = Queue()

        # Click affine transform points for image1
        msg = 'Click 3 feature points on the map!'
        t1 = threading.Thread(target=threaded_getCoord,args=(q1,imgStrava,3,msg,'Three coords of image1'))
        t1.start()

        time.sleep(3)

        # Click affine transform points for image2
        msg2 = 'Click the same 3 feature points on this map!'
        t2 = threading.Thread(target=threaded_getCoord,args=(q2,scaled_imgMap,3,msg2,'Three coords of image2'))
        t2.start()

        t1.join()
        t2.join()

        affPoints1 = q1.get()
        affPoints2 = q2.get()


        # Affine transform map image
        # affineT(imgStrava, scaled_imgMap, affPoints1, affPoints2)


        # Click control points to map and convert to map coordinates.
        affOutput = affineT(imgStrava, scaled_imgMap, affPoints1, affPoints2)
        msg3 = 'Click the control points from start to finish and press ESC'
        ctrlPoints = getCoord(affOutput, 999, msg3, 'Control points')
        
        # Delete temp files
        if os.path.isdir(temp_dir):
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                # Check if it's a file or a symlink
                if os.path.isfile(file_path) or os.path.islink(file_path):  
                    os.unlink(file_path)
            os.rmdir(temp_dir)

        # Close magnifier
        magnify.terminate()

        # Re-plot activity on map
        m = folium.Map(zoomSnap=0.001, zoomControl=False,
                       attributionControl=False)

        folium.PolyLine(activity['map.polyline'], color='red', weight=2).add_to(m)
        m.fit_bounds([sw, ne], padding=bound_pad)

        # List of converted coordinates for JSON export
        ctrlCoords = []

        # Add control points to map
        for i in range(len(ctrlPoints)):
            
            x = ctrlPoints[i][0]
            y = ctrlPoints[i][1]
            
            coord = pixel_to_coord(x, y, width, height, ne, sw)
            coord = [coord[0], coord[1]]
            
            ctrlCoords.append(coord)
            
            folium.Circle(
                radius=40,
                location=coord,
                color='magenta',
                fill=False,
                ).add_to(m)
            
            # Add a marker with control point number
            if i == 0:
                text = 'Start'
            elif i == len(ctrlPoints)-1:
                text = 'End'
            else:
                text = i
                
            n_offset = 0.0008
            
            folium.Marker(
                location=[coord[0]+n_offset, coord[1]+n_offset],
                icon=DivIcon(
                    icon_size=(150,36),
                    icon_anchor=(0,0),           
                    html = f'<div style="font-size: 18pt">{text}</div>',
                )
            ).add_to(m)


        # Define the output directory
        output_dir = 'output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Convert the list to JSON format and write file
        json_data = json.dumps(ctrlCoords)
        with open(os.path.join(output_dir, 'ctrlcoords.json'), 'w') as file:
            file.write(json_data)
        
        # Save the map and open in browser
        m.save(os.path.join(output_dir, 'final_map.html'))   
        webbrowser.open_new_tab(os.path.join(output_dir, 'final_map.html'))


root = tk.Tk()
app = Application(master=root)
app.mainloop()

