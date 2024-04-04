from env import PATH, PATHS, logging_level
import logging
from color_detection import color_detector as cd
from datetime import datetime
import json
import os

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging_level)


def write_to_file(positions_json, i):
    file_name = f"positions_config_{i}.json"
    file_path = os.path.join('testdata', file_name)
    with open(file_path, 'w') as file:
        json.dump(positions_json, file)


i = 0
for PATH in PATHS:
    logging.info(f"analyzed video: {PATH}")
    i = i+1

    positions = cd.analyze_cube_positions_from_video(PATH)
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    positions_json = {'time': time, 'config': positions}

    write_to_file(positions_json, i)

    # break
    # red = Kontur(ImageProcessing(frame), 'red')


