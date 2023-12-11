# -*- coding: utf-8 -*-
"""

Gets Strava activity from the input parameters

"""

import requests
import urllib3
import pandas as pd
import polyline
import re

def fetchStrava(stravaUrl, client_id, client_secret, refresh_token):
    # Check if the URL is correctly formatted
    if not re.match(r'^https://www\.strava\.com/activities/\d+$', stravaUrl):
        print("Error: Invalid URL.")
        return None

    try:
        # disable warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # define function to get a new access token
        def get_access_token(client_id, client_secret, refresh_token):
            oauth_url = 'https://www.strava.com/oauth/token'
            payload = {
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token',
                'f': 'json',
            }
            r = requests.post(oauth_url, data=payload, verify=False)
            access_token = r.json()['access_token']
            return access_token

        # get new access token
        access_token = get_access_token(client_id, client_secret, refresh_token)

        # A function to get one activity by url
        def get_activity_by_id(access_token, activity_id):
            activity_url = (
                f'https://www.strava.com/api/v3/activities/{activity_id}')
            headers = {'Authorization': 'Bearer ' + access_token}
            response = requests.get(
                activity_url,
                headers=headers
            )
            # Check if the request was successful
            response.raise_for_status()
            data = response.json()
            return data

        # split URL to id
        activity_id = int(stravaUrl.split('/')[-1])

        # get activity
        data = get_activity_by_id(access_token, activity_id)

        # data to dictionary
        data_dictionaries = [data]

        # normalize data
        activities = pd.json_normalize(data_dictionaries)

        # add decoded summary polylines
        activities['map.polyline'] = activities['map.summary_polyline'].apply(
            polyline.decode)

        # convert data types
        activities.loc[:, 'start_date'] = pd.to_datetime(
            activities['start_date']).dt.tz_localize(None)
        activities.loc[:, 'start_date_local'] = pd.to_datetime(
            activities['start_date_local']).dt.tz_localize(None)

        # convert values
        activities.loc[:, 'distance'] /= 1000  # convert from m to km
        activities.loc[:, 'average_speed'] *= 3.6  # convert from m/s to km/h
        activities.loc[:, 'max_speed'] *= 3.6  # convert from m/s to km/h

        # set index
        activities.set_index('start_date_local', inplace=True)

        # drop columns
        activities.drop(
            [
                'map.summary_polyline',
                'resource_state',
                'external_id',
                'upload_id',
                'location_city',
                'location_state',
                'has_kudoed',
                'start_date',
                'athlete.resource_state',
                'utc_offset',
                'map.resource_state',
                'athlete.id',
                'visibility',
                'heartrate_opt_out',
                'upload_id_str',
                'from_accepted_tag',
                'map.id',
                'manual',
                'private',
                'flagged',
            ],
            axis=1,
            inplace=True
        )

        activity = activities.iloc[0, :]  # first activity (most recent) if many

        return activity

    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
        return None
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
        return None
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
        return None
    except requests.exceptions.RequestException as err:
        print ("Something went wrong with the request:",err)
        return None
    except ValueError:
        print("Error: Invalid activity ID.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
