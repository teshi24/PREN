from env import PATH, PATHS, logging_level
import logging
from color_detection import color_detector as cd

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging_level)

i = 0
for PATH in PATHS:
    logging.info(f"analyzed video: {PATH}")
    i = i+1
    frame = cd.analyze_cube_video(PATH, i)
    # break
  #  red = Kontur(ImageProcessing(frame), 'red')


