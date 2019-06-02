#!/usr/bin/env python3

import json
import argparse
from typing import List, Dict
import sys
import re

import requests

sys.path.append('..')

import exceptions

STATISTICS_KEYS = ['viewCount', 'dislikeCount', 'favoriteCount', 'commentCount']
SNIPPET_KEYS = ['title', 'description', 'publishedAt', 'categoryId', 'tags']
CONTENT_DETIALS_KEYS = ['duration', 'regionRestriction', 'contentRating']

def _check_response_status(status_code: int):
	if status_code >= 400:
		raise exceptions.HTTPError('http status code: {}'.format(status_code))


def convert_duration(iso_duration: str) -> str:
	"""
	Convert iso-8691 duration to 'hh:mm:ss'
	
	Args:
		iso_duration (str): iso-8691 formated duration
	
	Returns:
		str: time with pretty formating
	"""
	match = re.search('^PT([0-9]+H)?([0-9]+M)?([0-9]+S)?', iso_duration)

	def parse(s):
		return '00' if s is None else s[0:len(s)-1].zfill(2)

	h = parse(match.group(1))
	m = parse(match.group(2))
	s = parse(match.group(3))

	return '{}:{}:{}'.format(h,m,s)


def get_video_data(api_key: str, videoList: List,
	print_progress: bool = True, progress_mult: int = 500) -> Dict:
	"""
	Get meta-data about videos by videoID
	
	Args:
		api_key (str): YouTube API key
		videoList (List): List of video IDs
	"""
	ret = dict()
	results_per_page = 50
	total = len(videoList)
	_progress_mult =  results_per_page * round(progress_mult/results_per_page)
	
	base_url = 'https://www.googleapis.com/youtube/v3/videos'
	params = {'key':api_key, 'part':'snippet,statistics,contentDetails',
	'maxResults': results_per_page}

	def _get_keys(d: Dict, keys: Dict):
		return {k:d[k] for k in keys if k in d.keys()}

	begin = 0
	end = 0
	while(True):
		begin = end
		end = begin + results_per_page
		params['id'] = ','.join(videoList[begin:end])
		
		response = requests.get(base_url, params)
		_check_response_status(response.status_code)
		d = response.json()
		
		for item in d['items']:
			ret[item['id']] = dict()

			#snippet data
			ret[item['id']].update(_get_keys(item['snippet'], SNIPPET_KEYS))

			#get stats
			ret[item['id']].update(_get_keys(item['statistics'], STATISTICS_KEYS))

			#content details
			ret[item['id']].update(_get_keys(item['contentDetails'], CONTENT_DETIALS_KEYS))

		
		if print_progress and (len(ret) % _progress_mult == 0):
			sys.stdout.write('\treceived {} of {}...\n'.format(len(ret), total))
		
		if end >= total:
			break
	
	if print_progress:
		sys.stdout.write('\treceived {}\nDone!\n'.format(len(ret)))

	return ret


def get_categories_dict(api_key: str) -> Dict:
	"""
	Get video category titles.
	
	Args:
		api_key (str): YouTube API key
	
	Returns:
		Dict: key, value pairs of videoCategory IDs and category titles
	"""
	base_url = 'https://www.googleapis.com/youtube/v3/videoCategories'
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
	
	categories_dict = get_categories_dict(par['api_key'])
	
	#i = 0
	#videosList[i]['videos'] = videosList[i]['videos'][0:150]
	
	for i in range(len(videosList)):
		sys.stdout.write('Getting video data for: {}.\n{} videos total.\n'.format(videosList[i]['title'], len(videosList[i]['videos'])))
		video_data = get_video_data(par['api_key'], videosList[i]['videos'])
		
		for k, v in video_data.items():
			video_data[k]['duration'] = convert_duration(v['duration'])
			video_data[k]['categoryStr'] = categories_dict[v['categoryId']]
		
		videosList[i]['video_data'] = video_data

	with open(args.ofname, 'w') as outF:
		json.dump(videosList, outF, indent=4, sort_keys=True)

if __name__ == '__main__':
	main()
