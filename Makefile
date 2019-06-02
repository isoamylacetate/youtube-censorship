
PYTHON_PATH = /usr/bin/env python3

PYTHON_FILES = $(wildcard **/*.py)

#data files
VIDEO_IDS = data/external/video_ids.json
VIDEO_DATA = data/external/video_data.json

.PHONY: video_ids

TARGETS = $(VIDEO_IDS) $(VIDEO_DATA) requirements.txt

all: $(TARGETS)

requirements.txt : $(PYTHON_FILES)
	pipreqs --force .

$(VIDEO_IDS) : params.json src/data/get_channel_videos.py
	cd src/data && $(PYTHON_PATH) get_channel_videos.py -o ../../data/external/video_ids.json ../../params.json

$(VIDEO_DATA) : src/data/get_video_data.py data/external/video_ids.json
	cd src/data && $(PYTHON_PATH) get_video_data.py -o ../../data/external/video_data.json ../../params.json ../../data/external/video_ids.json

