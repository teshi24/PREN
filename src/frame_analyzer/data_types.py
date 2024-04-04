import logging
from enum import Enum
from dataclasses import dataclass

cube_max_width = 300
cube_max_height = 300


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
