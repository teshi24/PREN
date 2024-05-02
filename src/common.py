import queue
import threading

from env import PATH, PATHS, logging_level
import logging
from frame_analyzer import color_detector as cd
from frame_analyzer import position_analyzer as pa
from datetime import datetime
import json
import os

from referencearea_detection import referencearea_detection as ref_area
from src.path_finder.path_finder import find_best_path
from src.referencearea_detection.referencearea_detection import get_image_and_angle

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging_level)


def write_to_file(positions_json, i):
    file_name = f"positions_config_{i}.json"
    file_path = os.path.join('testdata', file_name)
    with open(file_path, 'w') as file:
        json.dump(positions_json, file)


# def analyze_frames(frame_queue: queue):
#     logging.info('img 0')
#     (frame, angle) = frame_queue.get()
#     logging.debug(angle)
#     logging.info('img 1')
#     (frame1, angle1) = frame_queue.get()
#     logging.debug(angle1)
#     logging.info('img 2')
#     (frame2, angle2) = frame_queue.get()
#     logging.debug(angle2)
#     logging.info('img 3')
#     (frame3, angle3) = frame_queue.get()
#     logging.debug(angle3)
#
#     logging.info('position analysis starting')
#     positions = pa.analyze_cube_positions_per_frames(frame, angle, frame1, angle1, frame2, angle2, frame3, angle3)
#     logging.info('position analysis done')
#
#     time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     positions_json = {'time': time, 'config': positions}
#     logging.debug('write to file...')
#     write_to_file(positions_json, 10)
#
#     logging.info('positions written to file')
#
#
# logging.info('open queue')
# frame_queue = queue.Queue()
#
# logging.info('fill queue')
# # get_image_and_angle(frame_queue)
#
# running = threading.Event()
# running.set()
# find_frame_thread = threading.Thread(target=get_image_and_angle, args=(frame_queue, running))
# find_frame_thread.start()
#
# analyze_frames_thread = threading.Thread(target=analyze_frames, args=[frame_queue])
# analyze_frames_thread.start()
#
# analyze_frames_thread.join()
# running.clear()
# find_frame_thread.join()

i = 0
for PATH in PATHS:
    logging.info(f"analyzed video: {PATH}")
    i = i + 1

    positions = pa.analyze_cube_positions_from_video(PATH)
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    positions_json = {'time': time, 'config': positions}
    write_to_file(positions_json, i)

    path = find_best_path(positions)

    # break
    # red = Kontur(ImageProcessing(frame), 'red')
