#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 26 18:29:17 2019

@author: Aaron
"""

import requests
import argparse
import sys
import json

sys.path.append('..')

import exceptions

CHANEL_INFO_KEYS = ['title', 'description', 'customUrl', 'publishedAt', 'country']

def _check_response_status(status_code: int):
    if status_code >= 400:
        raise exceptions.HTTPError('http status code: {}'.format(status_code))


def get_channel_data(api_key: str, user_name: str = None, channel_id: str = None) -> dict:
    """
    Get the ID for the uploads playlist for a given channel. 
    Either the legacy user name or channel id must be supplied. 
    If both are supplied, the channel_id takes precedence.
    
    Args:
        api_key (str): YouTube API key
        user_name (str, optional): channel user name
        channel_id (str, optional): channel id
    
    Returns:
        dict: Chanel metadata
    
    Raises:
        ArgumentError: Required arguments not provided
        HTTPError: YouTube API get request returned an http error
    """
    
    ret = dict()
    base_url = 'https://www.googleapis.com/youtube/v3/channels'
    
    #init params
    params = dict()
    params['key'] = api_key
    params['part'] = 'snippet,contentDetails'
    if channel_id is not None:
        params['id'] = channel_id
    elif user_name is not None:
        params['forUsername'] = user_name
    else:
        raise exceptions.ArgumentError('user_name or channel_id required!')
    
    #make get request and return data
    response = requests.get(base_url, params)
    _check_response_status(response.status_code)
    dat = response.json()['items'][0]
    ret['uploads_playlistId'] = dat['contentDetails']['relatedPlaylists']['uploads']
    for d in CHANEL_INFO_KEYS:
        try:
            ret[d] = dat['snippet'][d]
        except KeyError:
            ret[d] = 'NA'
    
    return ret


def get_channel_videos(api_key: str, uploads_id: str,
                       print_progress: bool = True,
                       progress_mult = 500) -> list:
    """
    Get a list of video IDs for a channel.
    
    Args:
        api_key (str): YouTube API key
        uploads_id (str): ID of uploads playlist for channel
        print_progress (bool, optional): Should progress be printed?
        progress_mult (int, optional): How often should progress be printed. 
        Value is rounded to the nearest multiple of 50.

    Returns:
        list: List of video IDs for the channel
    """

    ret = []
    results_per_page = 50
    total = 0
    _progress_mult =  results_per_page * round(progress_mult/results_per_page)

    if print_progress:
        sys.stdout.write('Getting video list from channel: {}\n'.format(uploads_id))
    
    def _make_request() -> str:
        response = requests.get(base_url, params)
        _check_response_status(response.status_code)
        dat = response.json()
        for i in [x['contentDetails']['videoId'] for x in dat['items']]:
            ret.append(i)
        
        if print_progress and (len(ret) % _progress_mult == 0):
            total = dat['pageInfo']['totalResults']
            sys.stdout.write('\treceived {} of {}...\n'.format(len(ret), total))
        
        return '' if 'nextPageToken' not in dat.keys() else dat['nextPageToken']

    #set up request params
    base_url = 'https://www.googleapis.com/youtube/v3/playlistItems'
    params = {'key': api_key, 'part': 'contentDetails', 'playlistId': uploads_id,
        'maxResults': results_per_page}

    tok = _make_request()
    while True:
        if tok == '':
            break
        params['pageToken'] = tok
        tok = _make_request()
        
    if print_progress:
        sys.stdout.write('\treceived {}\nDone!\n'.format(len(ret)))
    
    return list(set(ret))


def writeVideoList(videoList: list, ofname: str):
    outF = open(ofname, 'w')
    json.dump(videoList, outF, indent=4, sort_keys=True)


def main():
    parser = argparse.ArgumentParser(description = 'Get a list of all uploads for a YouTube channel.')

    #parser.add_argument('-o', '--output', help = 'output file type', choices = ['tsv', 'sql3'])
    #parser.add_argument('-t', default = 'channel_id', help = 'Type of input')
    parser.add_argument('-o', '--ofname', default = 'video_ids.json', help = 'Output file name')
    parser.add_argument('params_file', help = 'Path to params file', type = str)

    args = parser.parse_args()
    with open(args.params_file, 'r') as inF:
        par = json.load(inF)

    #get ids of uploads playlists
    api_key: str = par['api_key']
    channels = list()
    for i in par['channels']['channel_ids']:
        channels.append(get_channel_data(api_key, channel_id = i))
    for u in par['channels']['user_names']:
        channels.append(get_channel_data(api_key, user_name = u))

    for i in range(len(channels)):
        channels[i]['videos'] = get_channel_videos(api_key, channels[i]['uploads_playlistId'])        

    writeVideoList(channels, '../../data/external/video_ids.json')

if __name__ == "__main__":
    main()


