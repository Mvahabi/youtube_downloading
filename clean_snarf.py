'''
_______________________________________________________________________________________________________
snarf.py - YouTube Channel Information Retrieval and Posting Tool
Copyright (C) Mahyar Vahabi - All Rights Reserved
Description: This program retrieves and processes YouTube channel information using the yt_dlp library.
It can dump channel information, write it to a file, and post it to an admin service.
Date: May, 2023

All rights reserved. No part of this program may be reproduced, distributed, or transmitted in any form
or by any means, including photocopying, recording, or other electronic or mechanical methods,
without the prior written permission of the author, except in the case of brief quotations embodied in
critical reviews and certain other noncommercial uses permitted by copyright law.

For permission requests, contact the author at mahyarvahabi@gmail.com.
_______________________________________________________________________________________________________
'''

import yt_dlp
import argparse
import requests
import json
import http.client
import ssl
import urllib3

def get_channel_info(creator_id):
    ydl_opts = {
        'ignoreerrors': True,
        'no_warnings': True,
        'extract_flat': True,
        'playlist_items': '1-10',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        channel_url = 'https://www.youtube.com/@{}'.format(creator_id)
        info = ydl.extract_info(channel_url, download=False)
        videos = info.get('entries', [])
        result = videos[:9]
    return result
    
def dump_info(channel_info):
    print("Dumping Channel Info:")
    print(json.dumps(channel_info, indent=4))

def write_info(channel_info, creator_id, filename):
    with open(filename, 'w+') as file:
        file.write("Channel Information for @{}:\n".format(creator_id))
        file.write(json.dumps(channel_info, indent=4))
    print("Channel info written to file: {}".format(filename))

#_____________________________________________________________________________________

def get_csrf_token():
    url = "https://35.161.49.69/ws/v1/auth-user"
    headers = {
        "Referer": "https://35.161.49.69",
    }

    response = requests.get(url, headers=headers, verify=False)
    csrf_token = None

    if response.status_code == 200:
        csrf_token = response.cookies.get("csrftoken")
        
    return csrf_token

def get_creators():
    host = "35.161.49.69"  # Hardcoded IP address
    endpoint = "/ws/v1/rest/creator/"
    url = f"https://{host}{endpoint}"
    headers = {
        "Referer": host,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        creators = response.json()
        for creator in creators:
            creator_id = creator.get("id")
            creator_name = creator.get("name")
            print(f"Creator ID: {creator_id}, Name: {creator_name}")
    else:
        print("Failed to retrieve creators. Status code: {}".format(response.status_code))

def create_creator(name):
    creators = get_creators()
    existing_creator = next((creator for creator in creators if creator["name"] == name), None)

    if existing_creator:
        print("Creator already exists.")
        print(f"Creator ID: {existing_creator['id']}, Name: {existing_creator['name']}")
    else:
        host = "35.161.49.69"  # Hardcoded IP address
        endpoint = "/ws/v1/rest/creator/"
        url = f"https://{host}{endpoint}"
        headers = {
            "Referer": host,
            "Content-Type": "application/json",
            "X-CSRFToken": get_csrf_token()
        }
        data = {
            "name": name
        }
        response = requests.post(url, json=data, headers=headers, verify=False)

        if response.status_code == 200:
            creator = response.json()
            creator_id = creator.get("id")
            creator_name = creator.get("name")
            print(f"Created Creator - ID: {creator_id}, Name: {creator_name}")
        else:
            print("Failed to create creator. Status code: {}".format(response.status_code))

def get_creator_by_id(creator_id):
    host = "35.161.49.69"  # Hardcoded IP address
    endpoint = "/ws/v1/rest/creator/{creator_id['id']}"
    url = f"https://{host}{endpoint}"
    headers = {
        "Referer": host,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        creator = response.json()
        creator_id = creator.get("id")
        creator_name = creator.get("name")
        print(f"Creator ID: {creator_id}, Name: {creator_name}")
    else:
        print("Failed to retrieve creator. Status code: {}".format(response.status_code))

def replace_creator(creator_id, new_name):
    host = "35.161.49.69"  # Hardcoded IP address
    endpoint = "/ws/v1/rest/creator"
    url = f"https://{host}{endpoint}"
    headers = {
        "Referer": "https://35.161.49.69",
        "Content-Type": "application/json",
        "X-CSRFToken": get_csrf_token()  
    }
    data = {
        "name": new_name
    }

    response = requests.put(url, json=data, headers=headers, verify=False)

    if response.status_code == 200:
        creator_info = response.json()
        print("Creator replaced successfully.")
        print(f"New creator information: ID: {creator_info['id']}, Name: {creator_info['name']}")
    else:
        print(f"Failed to replace creator. Status code: {response.status_code}")


def update_creator(creator_id, name):
    url = f"https://35.161.49.69/ws/v1/rest/creator/{creator_id}"
    headers = {
        "Referer": "https://35.161.49.69",
        "Content-Type": "application/json",
        "X-CSRFToken": get_csrf_token()
    }
    data = {
        "name": name
    }

    response = requests.patch(url, json=data, headers=headers, verify=False)

    if response.status_code == 200:
        updated_creator = response.json()
        return updated_creator
    else:
        return None

def delete_creator(creator_id):
    url = f"https://35.161.49.69/ws/v1/rest/creator/{creator_id}"
    headers = {
        "Referer": "https://35.161.49.69",
        "Content-Type": "application/json",
        "X-CSRFToken": get_csrf_token()
    }

    response = requests.delete(url, headers=headers, verify=False)

    if response.status_code == 200:
        return True
    else:
        return False

#_____________________________________________________________________________________
def get_videos(creator_id):
    host = "35.161.49.69"  # Hardcoded IP address
    endpoint = f"/ws/v1/rest/creator/{creator_id['id']}/video"
    url = f"https://{host}{endpoint}"
    headers = {
        "Referer": host,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        videos = response.json()
        for video in videos:
            video_id = video.get("id")
            video_name = video.get("name")
            video_description = video.get("description")
            video_duration = video.get("duration")
            print(f"Video - ID: {video_id}, Name: {video_name}, Description: {video_description}, Duration: {video_duration}")
    else:
        print("Failed to get creator videos. Status code: {}".format(response.status_code))

# this function might be the hardest to write
def create_videos():
    return

def get_videos_id():
    return

def replace_videos():
    return

def update_videos():
    return

def delete_video():
    return
#_____________________________________________________________________________________

'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Retrieve and process YouTube channel information')
    parser.add_argument('creator_id', type=str, help='ID of the YouTube creator')
    parser.add_argument('--dump', action='store_true', help='Dump channel info to screen')
    parser.add_argument('--write', type=str, help='Write channel info to file')

    args = parser.parse_args()

    # set the reference youtube handler passed by user input
    creator_id = args.creator_id

    # Step 1: Get channel info + latests videos
    channel_info = get_channel_info(creator_id)

    # Step 2: Dump channel info to screen
    # in reality this should dump channel_info but because of how long it is I decided to just return the creator ID for now
    if args.dump:
        dump_info(creator_id)
        #dump_info(channel_info)

    # Step 3: Write channel info to file
    if args.write:
        write_info(channel_info, creator_id, args.write)
'''

def main():
    parser = argparse.ArgumentParser(description='Retrieve and process YouTube channel information')
    parser.add_argument('--get-creators', action='store_true', help='Get a list of creators')
    parser.add_argument('--create-creator', type=str, help='Create a creator')
    parser.add_argument('--get-creator-by-id', type=str, help='Get a creator by ID')
    parser.add_argument('--replace-creator', nargs=2, metavar=('creator_id', 'new_name'), help='Replace a creator by ID')
    parser.add_argument('--update-creator', nargs=2, metavar=('creator_id', 'name'), help='Update fields in a creator by ID')
    parser.add_argument('--delete-creator', type=str, help='Delete a creator by ID')

    args = parser.parse_args()

    # Server Tools
    if args.get_creators:
        get_creators()

    if args.create_creator:
        create_creator(args.create_creator)

    if args.get_creator_by_id:
        get_creator_by_id(args.get_creator_by_id)

    if args.replace_creator:
        replace_creator(args.replace_creator[0], args.replace_creator[1])

    if args.update_creator:
        update_creator(args.update_creator[0], args.update_creator[1])

    if args.delete_creator:
        delete_creator(args.delete_creator)

if __name__ == '__main__':
    main()