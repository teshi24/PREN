from env import PATH, PATHS, logging_level
import logging
from color_detection import color_detector as cd

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging_level)

for PATH in PATHS:
    logging.info(f"analyzed video: {PATH}")
    frame = cd.analyze_cube_video(PATH)
    # break
  #  red = Kontur(ImageProcessing(frame), 'red')


