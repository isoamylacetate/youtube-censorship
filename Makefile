
PYTHON_PATH = /usr/bin/env python3

PYTHON_FILES = $(wildcard **/*.py)

#data files
VIDEO_IDS = data/external/video_ids.json

.PHONY: video_ids

TARGETS = $(VIDEO_IDS) requirements.txt

all: $(TARGETS)

requirements.txt : $(PYTHON_FILES)
	pipreqs --force .

$(VIDEO_IDS) : params.json src/data/get_channel_videos.py
	cd src/data && $(PYTHON_PATH) get_channel_videos.py -o ../../data/external/video_ids.json ../../params.jsonc

