# ReplayO: Mark Controls
Helper program to mark orienteering control points from a paper map, and view them 
with Strava activity.

## Description
WINDOWS ONLY, NOT TESTED WITH ANYTHING ELSE YET!

I'm newbie coder and this is my first proper program, I got a lot to learn.

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
4. Click three same map feature points from both maps in the same order. You may need to do this 
   several times to get a good result.
5. Press ESC-key to exit the preview window
6. Click first the start, then all the controls in right order, and last the finish. 
   When you are done, hit ESC.
7. Your track with control points opens in a browser window, or manually open output/final_map.html file.

WIP: 
- GPX file input 
- OAuth
- A lot of improvements and fixes
- A web app to replay animated Strava activity and compare with friends activity.
