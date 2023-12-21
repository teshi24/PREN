from env import PATH, PATHS

from color_detection import color_detector as cd

i = 0

for PATH in PATHS:
    print(++i)
    frame = cd.analyze_cube_video(PATH)
    # break
  #  red = Kontur(ImageProcessing(frame), 'red')


