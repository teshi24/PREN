from env import PATH, PATHS

from color_detection import color_detector as cd, draw_lines as dl
from src.color_detection.draw_lines import Kontur, ImageProcessing

i = 0

for PATH in PATHS:
    print(++i)
    frame = cd.getFrame(PATH)
    # break
  #  red = Kontur(ImageProcessing(frame), 'red')


