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

    angle = 45
    frame = ref_area.get_image_by_angle(angle, PATH)

    angle1 = angle + 90
    frame1 = ref_area.get_image_by_angle(angle1, PATH)

    angle2 = angle1 + 90
    frame2 = ref_area.get_image_by_angle(angle2, PATH)

    angle3 = angle2 + 90
    frame3 = ref_area.get_image_by_angle(angle3, PATH)

    positions = pa.analyze_cube_positions_per_frames(frame, angle, frame1, angle1, frame2, angle2, frame3, angle3)
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    positions_json = {'time': time, 'config': positions}
    write_to_file(positions_json, 10+i)

    positions = pa.analyze_cube_positions_from_video(PATH)
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    positions_json = {'time': time, 'config': positions}

    write_to_file(positions_json, i)

    # break
    # red = Kontur(ImageProcessing(frame), 'red')


