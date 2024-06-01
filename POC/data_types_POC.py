import logging
from enum import Enum
from dataclasses import dataclass

import numpy as np

# todo: check those values
# video values
# cube_max_width = 300
# cube_max_height = 300
cube_max_width = 160
cube_max_height = 160

# hell #F74049           (357°, 74%, 97%) -- hsv(357, 74%, 97%)
# weiss #B4454A          (356°, 62%, 71%)
# saturated #F6323E      (355°, 80%, 96%)
# dark saturated #A21D25 (355°, 82%, 64%) -- hsv(356, 82%, 64%)
# hell detected #F83640  (356°, 78%, 97%)
# dark detected #9C1E1F  (359°, 81%, 61%)

# Lower Hue Range (0° - 10°)
# Lower Bound: (0°, 62%, 61%)
# Upper Bound: (10°, 82%, 97%)
# Upper Hue Range (350° - 360°)
# Lower Bound: (350°, 62%, 61%)
# Upper Bound: (360°, 82%, 97%)
yellow_lower = np.array([20, 140, 50])
yellow_upper = np.array([50, 255, 255])
blue_lower = np.array([75, 110, 84])
blue_upper = np.array([145, 255, 255])
red_lower1 = np.array([0, 120, 120])
red_upper1 = np.array([10, 255, 255])
red_lower2 = np.array([170, 60, 40])
red_upper2 = np.array([180, 255, 255])


@dataclass
class ColorData:
    color_name: str
    rgb_value: tuple


class Color(ColorData, Enum):
    RED = 'red', (0, 0, 255)
    BLUE = 'blue', (255, 0, 0)
    YELLOW = 'yellow', (0, 255, 255)
    NONE = 'none', ()


class Cube:
    def __init__(self, color, x, y, w, h):
        self.color = color
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.cx = int(x + w / 2)
        self.cy = int(y + h / 2)
        self.center = (self.cx, self.cy)
        self.left_top = (x, y)
        self.right_top = (x + w, y)
        self.right_bottom = (x + w, y + h)
        self.left_bottom = (x, y + h)

    def log_values(self):
        logging.debug("----------------------")
        logging.debug("color: " + self.color.color_name)
        logging.debug("x: " + str(self.x))
        logging.debug("y: " + str(self.y))
        logging.debug("w: " + str(self.w))
        logging.debug("h: " + str(self.h))
        logging.debug("center       (cx, cy):       " + str(self.center))
        logging.debug("left top     (x, y):         " + str(self.left_top))
        logging.debug("right top    (x + w, y):     " + str(self.right_top))
        logging.debug("right bottom (x + w, y + h): " + str(self.right_bottom))
        logging.debug("left bottom  (x, y + h):     " + str(self.left_bottom))

    def width_in_range(self):
        return self.w < cube_max_width

    def height_in_range(self):
        return self.h < cube_max_height
