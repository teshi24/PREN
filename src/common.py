from env import PATH, PATHS, logging_level
import logging
from frame_analyzer import color_detector as cd
from frame_analyzer import position_analyzer as pa
from datetime import datetime
import json
import os

from referencearea_detection import referencearea_detection as ref_area

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

    # angle = 45
    # ref_area.get_image_by_angle(angle, PATH)
    #
    # angle = angle + 45
    # ref_area.get_image_by_angle(angle, PATH)
    #
    # angle = angle + 45
    # ref_area.get_image_by_angle(angle, PATH)
    #
    # angle = angle + 45
    # ref_area.get_image_by_angle(angle, PATH)


    positions = pa.analyze_cube_positions_from_video(PATH)
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    positions_json = {'time': time, 'config': positions}

    write_to_file(positions_json, i)

    # break
    # red = Kontur(ImageProcessing(frame), 'red')


