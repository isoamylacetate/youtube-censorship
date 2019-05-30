#!/usr/bin/env python3

import json
import argparse
from typing import List, Dict

import requests

STATISTICS_KEYS = ['viewCount', 'dislikeCount', 'favoriteCount', 'commentCount']
SNIPPET_KEYS = ['title', 'description', 'publishedAt', 'categoryId']

def _check_response_status(status_code: int):
	if status_code >= 400:
		raise exceptions.HTTPError('http status code: {}'.format(status_code))


def get_video_data(api_key: str, videoList: List) -> Dict:
	"""
	Get meta-data about videos by videoID
	
	Args:
	    api_key (str): YouTube API key
	    videoList (List): List of video IDs
	"""
	base_url = 'https://www.googleapis.com/youtube/v3/videoCategories'
	params = {'key':api_key, 'id':video, 'part':'statistics'}


	response = requests.get(base_url, params)
	_check_response_status(response.status_code)
	

	
	#snippet data


	#get stats
	stats_dict = d['items'][0]['statistics']
	ret.update({k:stats_dict[k] for k in STATISTICS_KEYS if k in stats_dict.keys()})

return ret


def get_categories_dict(api_key: str) -> Dict:
	"""
	Get video category titles.
	
	Args:
	    api_key (str): YouTube API key
	
	Returns:
	    Dict: key, value pairs of videoCategory IDs and category titles
	"""
	base_url = 'https://www.googleapis.com/youtube/v3/videos'
	params = {'key':api_key, 'part':'snippet', 'regionCode':'US'}

	response = requests.get(base_url, params)
	_check_response_status(response.status_code)

	return {i['id']: i['snippet']['title'] for i in response.json()['items']} 

def main():
	parser = argparse.ArgumentParser(description = 'Lookup data for videos ')

	parser.add_argument('-o', '--ofname', default = 'video_ids.json', help = 'Output file name')
	parser.add_argument('params_file', help = 'Path to params file', type = str)
	parser.add_argument('input_file', type = str, help = 'Path to input file.')

	#get input files
	args = parser.parse_args()
	with open(args.params_file, 'r') as inF:
		par = json.load(inF)
	with open(args.input_file, 'r') as inF:
		videosList = json.load(inF)



if __name__ == '__main__':
	main()
