from datetime import datetime
import json
import os
import logging
from dataclasses import dataclass
from enum import Enum
import cv2
import numpy as np
from typing import Dict, Type

from env import logging_level

cube_max_width = 300
cube_max_height = 300

# HSV filters
blue_lower = np.array([75, 95, 84])
blue_upper = np.array([145, 255, 255])
red_lower1 = np.array([0, 130, 130])
red_upper1 = np.array([10, 255, 255])
red_lower2 = np.array([170, 70, 50])
red_upper2 = np.array([180, 255, 255])
yellow_lower = np.array([20, 140, 50])
yellow_upper = np.array([50, 255, 255])


def detect_color(image, lower_bound1, upper_bound1, lower_bound2=None, upper_bound2=None, min_area=700):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound1, upper_bound1)
    if lower_bound2 is not None:
        mask = cv2.add(cv2.inRange(hsv, lower_bound2, upper_bound2), mask)

    # Morphologische Operationen
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    mask = cv2.erode(mask, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
    # contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    # Filtern der Konturen nach Fläche
    # ih, iw, ic = image.shape
    # min_area = ih * iw / 400
    # min_area = 500
    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

    return filtered_contours


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


class PositionIdentifier:
    def __init__(self,
                 calibration_cube: Cube,
                 position_in_frame: int,
                 prerequisite: int | None = None,
                 hidden_by: [[int]] = None):
        self.calibrationCube = calibration_cube
        self.toleranceXAxis = 35
        self.toleranceYAxis = 85
        self.position = position_in_frame
        self.prerequisite = prerequisite
        self.hidden_by = hidden_by

    def is_cube_at_position(self, cube: Cube):
        return (self.__is_value_in_range(cube.x, self.calibrationCube.x, self.toleranceXAxis) and
                self.__is_value_in_range(cube.y, self.calibrationCube.y, self.toleranceYAxis) and
                self.__is_value_in_range(cube.cx, self.calibrationCube.cx, self.toleranceXAxis) and
                self.__is_value_in_range(cube.cy, self.calibrationCube.cy, self.toleranceYAxis))

    @staticmethod
    def __is_value_in_range(value: int, average: int, delta: int):
        lower_bound = average - delta
        upper_bound = average + delta
        return lower_bound <= value <= upper_bound

    # todo: handle hidden_by


# würfelposition: position_im_frame
# obere Fläche  0°             obere Fläche  90°                              obere Fläche  180°           obere Fläche  270°
# +-----+-----+                +-----+-----+                                 +-----+-----+                +-----+-----+
# | 7:7 | 6:6 |                | 8:7 | 7:6 |                                 | 5:7 | 8:6 |                | 6:7 | 5:6 |
# +-----+-----+                +-----+-----+                                 +-----+-----+                +-----+-----+
# | 8:8 | 5:5 |                | 5:8 | 6:5 |                                 | 6:8 | 7:5 |                | 7:8 | 8:5 |
# +-----+-----+                +-----+-----+                                 +-----+-----+                +-----+-----+
# untere Fläche                untere Fläche                                 untere Fläche                untere Fläche
# +-----+-----+                +-----+-----+                                 +-----+-----+                +-----+-----+
# | 3:3 | 2:2 |                | 4:3 | 3:2 | weisser Bereich weisser Bereich | 1:3 | 4:2 |                | 2:3 | 1:2 |
# +-----+-----+ --             +-----+-----+ --                           -- +-----+-----+             -- +-----+-----+
# | 4:4 | 1:1 |                | 1:4 | 2:1 |                                 | 2:4 | 3:1 |                | 3:4 | 4:1 |
# +-----+-----+                +-----+-----+                                 +-----+-----+                +-----+-----+
#     |      weisser Bereich                                                                    weisser Bereich |

defaultConfig: Dict[int, Type[PositionIdentifier | None]] = {
    1: None,
    2: None,
    3: None,
    4: None,
    5: None,
    6: None,
    7: None,
    8: None
}

# todo: add calibration algorithm

# todo: fix structure functionality
# position_structure_0_degree = {
#     1: PositionIdentifier(Cube(Color.NONE, 967, 411, 182, 162), 1), 2: PositionIdentifier(Cube(Color.NONE, 968, 244, 164, 98), 2),
#     3: None, 4: PositionIdentifier(Cube(Color.NONE, 781, 416, 184, 158), 4), # todo: find data for 3
#     5: PositionIdentifier(Cube(Color.NONE, 964, 183, 210, 258), 5), 6: PositionIdentifier(Cube(Color.NONE, 952, 100, 196, 100), 6),
#     7: PositionIdentifier(Cube(Color.NONE, 780, 98, 186, 126), 7), 8: PositionIdentifier(Cube(Color.NONE, 770, 177, 200, 274), 8)
# }
# def rotate_structure(structure, degrees):
#     rotated_structure = {}
#     for key, cube in structure.items():
#         rotated_key = rotate_key(key, degrees)
#         rotated_structure[rotated_key] = cube
#     return rotated_structure
#
# def rotate_key(key, degrees):
#     # Function to rotate the key based on degrees (0, 90, 180, 270)
#     if degrees == 90:
#         return (key - 1) // 2 * 4 + 2 - (key % 2)
#     elif degrees == 180:
#         return (key - 1) ^ 4 + 1
#     elif degrees == 270:
#         return (key - 1) // 2 * 4 + 1 + (key % 2)
#     else:
#         return key
#
# def print_structure(structure):
#     print("------")
#     for key, position_identifier in structure.items():
#         if position_identifier is None:
#             print(f'{key}: None')
#             continue
#         print(f'{key}: {position_identifier.position}')

# # Example usage
# initial_structure = position_structure_0_degree
# print_structure(initial_structure)
#
# # Rotate the structure by 90 degrees
# rotated_structure_90 = rotate_structure(initial_structure, 90)
# print_structure(rotated_structure_90)
#
# # Rotate the structure by 180 degrees
# rotated_structure_180 = rotate_structure(initial_structure, 180)
# print_structure(rotated_structure_180)
#
# # Rotate the structure by 270 degrees
# rotated_structure_270 = rotate_structure(initial_structure, 270)
# print_structure(rotated_structure_270)


# extra sortiert, damit andere Reihenfolge entdeckt wird
calibratedPositions0Degree = {
    8: PositionIdentifier(Cube(Color.NONE, 770, 177, 200, 274), 8, 4),
    5: PositionIdentifier(Cube(Color.NONE, 964, 183, 210, 258), 5, 1),
    7: PositionIdentifier(Cube(Color.NONE, 780, 98, 186, 126), 7, 3),
    6: PositionIdentifier(Cube(Color.NONE, 952, 100, 196, 100), 6, 2),
    3: None,  # PositionIdentifier(Cube(Color.NONE, 967, 411, 196, 100)),
    2: PositionIdentifier(Cube(Color.NONE, 968, 244, 164, 98), 2),
    1: PositionIdentifier(Cube(Color.NONE, 967, 411, 182, 162), 1),
    4: PositionIdentifier(Cube(Color.NONE, 781, 416, 184, 158), 4),
}

calibratedPositions90Degree = {
    5: calibratedPositions0Degree[8],
    6: calibratedPositions0Degree[5],
    8: calibratedPositions0Degree[7],
    7: calibratedPositions0Degree[6],
    4: calibratedPositions0Degree[3],
    3: calibratedPositions0Degree[2],
    2: calibratedPositions0Degree[1],
    1: calibratedPositions0Degree[4],
}
# würfelposition: position_im_per_frame
# obere Fläche  0°             obere Fläche  90°                              obere Fläche  180°           obere Fläche  270°
# +-----+-----+                +-----+-----+                                 +-----+-----+                +-----+-----+
# | 7:7 | 6:6 |                | 8:7 | 7:6 |                                 | 5:7 | 8:6 |                | 6:7 | 5:6 |
# +-----+-----+                +-----+-----+                                 +-----+-----+                +-----+-----+
# | 8:8 | 5:5 |                | 5:8 | 6:5 |                                 | 6:8 | 7:5 |                | 7:8 | 8:5 |
# +-----+-----+                +-----+-----+                                 +-----+-----+                +-----+-----+
# untere Fläche                untere Fläche                                 untere Fläche                untere Fläche
# +-----+-----+                +-----+-----+                                 +-----+-----+                +-----+-----+
# | 3:3 | 2:2 |                | 4:3 | 3:2 | weisser Bereich weisser Bereich | 1:3 | 4:2 |                | 2:3 | 1:2 |
# +-----+-----+ --             +-----+-----+ --                           -- +-----+-----+             -- +-----+-----+
# | 4:4 | 1:1 |                | 1:4 | 2:1 |                                 | 2:4 | 3:1 |                | 3:4 | 4:1 |
# +-----+-----+                +-----+-----+                                 +-----+-----+                +-----+-----+
#     |      weisser Bereich                                                                    weisser Bereich |

calibratedPositions180Degree = {
    6: calibratedPositions0Degree[8],
    7: calibratedPositions0Degree[5],
    5: calibratedPositions0Degree[7],
    8: calibratedPositions0Degree[6],
    1: calibratedPositions0Degree[3],
    4: calibratedPositions0Degree[2],
    3: calibratedPositions0Degree[1],
    2: calibratedPositions0Degree[4],
}
calibratedPositions270Degree = {
    7: calibratedPositions0Degree[8],
    8: calibratedPositions0Degree[5],
    6: calibratedPositions0Degree[7],
    5: calibratedPositions0Degree[6],
    2: calibratedPositions0Degree[3],
    1: calibratedPositions0Degree[2],
    4: calibratedPositions0Degree[1],
    3: calibratedPositions0Degree[4],
}


@dataclass
class CalibratedPosition:
    positions: Dict[int, PositionIdentifier]


class CalibratedPositions(CalibratedPosition, Enum):
    DEGREE_0 = calibratedPositions0Degree,
    DEGREE_90 = calibratedPositions90Degree,
    DEGREE_180 = calibratedPositions180Degree,
    DEGREE_270 = calibratedPositions270Degree,

    @classmethod
    def from_angle(cls, angle):
        if angle == 0:
            return cls.DEGREE_0
        elif angle == 90:
            return cls.DEGREE_90
        elif angle == 180:
            return cls.DEGREE_180
        elif angle == 270:
            return cls.DEGREE_270
        else:
            raise ValueError(f"Invalid angle: {angle}")


# for i in range(0, 8):
#     calibrated_position = calibratedPositions.get(i + 1)
#     if calibrated_position is None:
#         continue
#     calibrated_position.calibrationCube.printValues()

def split_cubes_next_to_each_other(cube: [Cube]):
    half_w = int(cube.w / 2)

    right_cube = Cube(cube.color, cube.x, cube.y, half_w, cube.h)
    left_cube = Cube(cube.color, cube.x + half_w, cube.y, half_w, cube.h)

    return [right_cube, left_cube]


def split_cubes_on_top_of_each_other(cube: [Cube]):
    half_h = int(cube.h / 2)

    right_cube = Cube(cube.color, cube.x, cube.y, cube.w, half_h)
    left_cube = Cube(cube.color, cube.x, cube.y + half_h, cube.w, half_h)

    return [right_cube, left_cube]


def split_big_cubes(cubes: [Cube]):
    clean_cubes: [Cube] = []

    for cube in cubes:
        width_in_range = cube.width_in_range()
        height_in_range = cube.height_in_range()
        if width_in_range and height_in_range:
            # cube standard size
            clean_cubes.append(cube)
            continue
        if not width_in_range:
            if not height_in_range:
                # todo: fix spezialfall - mit cnts analysieren
                clean_cubes.append(cube)
                continue
            # nebeneinander
            clean_cubes.extend(split_cubes_next_to_each_other(cube))
            continue
        # todo: fix spezialfall wahrscheinlich ober einander
        #       ! kann aber auch hintereinander sein !
        clean_cubes.extend(split_cubes_on_top_of_each_other(cube))

    return clean_cubes


def analyze_positions_in_one_frame(cubes: [Cube], angle):
    positions = defaultConfig.copy()

    calibrated_positions = CalibratedPositions.from_angle(angle).positions

    for cube in cubes:
        msg = "color: " + str(cube.color.color_name) + ", x: " + str(cube.x) + ", y: " + str(
            cube.y) + ", center: " + str(cube.center)
        logging.debug(msg)
        for key, position_identifier in calibrated_positions.items():
            msg1 = "calibratedPosition: " + str(position_identifier)
            logging.debug(msg1)
            if positions[key] is None and position_identifier is not None and position_identifier.is_cube_at_position(
                    cube):
                positions[key] = cube.color
                break

    log_positions("detected positions:", positions)

    # todo: fix prep
    # changed_positions = positions.copy()
    # for key in positions:
    #     color = positions[key]
    #     if color is None:
    #         continue
    #     calibratedPosition = calibrated_positions[key]
    #     print("analyzed item: " + str(key) + ': ' + str(positions[key]))
    #     if calibratedPosition is not None and calibratedPosition.prerequisite is not None: # and calibratedPosition.prerequisite is not None:
    #         print("calibration item as prerequisite: " + str(calibratedPosition.prerequisite) + ': ' + str(positions[calibratedPosition.prerequisite]))
    #         if positions[calibratedPosition.prerequisite] is not None:
    #             print("issue detected - invisible item was detected as a color; value set to None")
    #             changed_positions[key] = None
    #
    # print_positions("positions after changes:", changed_positions)
    return positions


def log_positions(analysis_name, positions):
    logging.info(analysis_name)
    position_string = "{ "
    for key in positions:
        color = positions[key]
        if color is None:
            position_string += str(key) + ": None,"
            continue
        position_string += str(key) + ": " + str(color.color_name) + ","
    position_string += " }"
    logging.info(position_string)


def get_cubes_from_frame(frame, angle, cv2):
    logging.debug("----------- getColorOfFrame -----------")
    blue_contours = detect_color(frame, blue_lower, blue_upper)
    red_contours = detect_color(frame, red_lower1, red_upper1, red_lower2, red_upper2)
    yellow_contours = detect_color(frame, yellow_lower, yellow_upper)

    cubes = []

    for cnt in blue_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cube = Cube(Color.BLUE, x, y, w, h)
        cv2 = draw_cube(cnt, cube, cv2, frame)
        cubes.append(cube)

    for cnt in red_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cube = Cube(Color.RED, x, y, w, h)
        cv2 = draw_cube(cnt, cube, cv2, frame)
        cubes.append(cube)

    for cnt in yellow_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cube = Cube(Color.YELLOW, x, y, w, h)
        cv2 = draw_cube(cnt, cube, cv2, frame)
        cubes.append(cube)

    if logging_level == logging.DEBUG:
        cv2.imshow('Video', frame)
        while cv2.waitKey(1) & 0xFF != ord('q'):
            continue
    return [cv2, cubes]


def draw_cube(cnt, cube, cv2, frame):
    cv2.rectangle(frame, cube.left_top, cube.right_bottom, cube.color.rgb_value, 2)
    cube.log_values()
    cv2.circle(frame, cube.center, 1, (255, 255, 255), -1)
    cv2.putText(frame, cube.color.color_name, cube.left_top, cv2.FONT_HERSHEY_SIMPLEX, 0.7, cube.color.rgb_value, 2)
    draw_contours(cnt, cv2, frame)
    return cv2


def draw_contours(cnt, cv2, frame):
    epsilon = 0.04 * cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, epsilon, True)
    logging.debug(approx)
    cv2.drawContours(frame, [approx], -1, (255, 255, 255), 2)


End_Result = {
    Color.RED.color_name: int,
    Color.BLUE.color_name: int,
    Color.YELLOW.color_name: int,
    Color.NONE.color_name: int
}


def analyze_video_positions(video_positions: [Dict[int, Type[PositionIdentifier | None]]]):
    logging.debug("analyze_video_positions started")
    starting_point = {Color.RED.color_name: 0,
                      Color.BLUE.color_name: 0,
                      Color.YELLOW.color_name: 0,
                      Color.NONE.color_name: 0}
    end_positions_percentages: Dict[int, End_Result] = {
        1: starting_point.copy(),
        2: starting_point.copy(),
        3: starting_point.copy(),
        4: starting_point.copy(),
        5: starting_point.copy(),
        6: starting_point.copy(),
        7: starting_point.copy(),
        8: starting_point.copy(),
    }

    for positions in video_positions:
        if positions is None:
            logging.debug('positions was None')
            continue
        msg = 'positions: ' + str(positions)
        logging.debug(msg)
        for key, color in positions.items():
            if key is None:
                logging.debug('key was None')
                continue
            if color is None:
                logging.debug('color was None')
                continue
            msg1 = 'key: ' + str(key)
            logging.debug(msg1)
            msg2 = 'color: ' + str(color)
            logging.debug(msg2)
            msg3 = 'color.color_name' + str(color.color_name)
            logging.debug(msg3)
            msg4 = 'end_positions_percentages[key]: ' + str(end_positions_percentages[key])
            logging.debug(msg4)
            msg5 = 'end_positions_percentages[key][color.color_name]: ' + str(
                end_positions_percentages[key][color.color_name])
            logging.debug(msg5)
            end_positions_percentages[key][color.color_name] += 25

    logging.debug("end result percentages")
    for end_position, colors in end_positions_percentages.items():
        msg6 = str(end_position) + ": " + str(colors)
        logging.debug(msg6)

    end_result = defaultConfig.copy()
    logging.info("end result")
    for end_position, colors in end_positions_percentages.items():
        most_probable_color = max(colors, key=colors.get)

        # Check if there are duplicates with the same highest value
        if list(colors.values()).count(colors[most_probable_color]) > 1:
            end_result[end_position] = ''
        else:
            end_result[end_position] = most_probable_color
    logging.info(end_result)
    now = datetime.now().strftime('%Y-%m-%d.%H.%M.%S')
    file_name = 'end_result_' + str(now) + '.json'
    file_path = os.path.join('testdata', file_name)
    with open(file_path, 'w') as file:
        json.dump(end_result, file)


def analyze_cube_video(path):
    # VideoCapture-Objekt erstellen und Video-Datei laden
    cap = cv2.VideoCapture(path)

    frame_count = 0
    angle = 0
    video_positions: [Dict[int, Type[PositionIdentifier | None]]] = []
    frame = None
    while True:
        if angle > 270:
            break

        ret, frame = cap.read()
        if not ret:
            break

        if frame_count != 0:
            frame_count = frame_count - 1
            continue
        else:
            # todo: check with angle detector whether we are good
            frame_count = 220

        [cv3, raw_cubes] = get_cubes_from_frame(frame, angle, cv2)
        cubes = split_big_cubes(raw_cubes)
        video_positions.append(analyze_positions_in_one_frame(cubes, angle))

        angle = angle + 90
        # if angle >= 270:
        # todo: remove
        # break
    analyze_video_positions(video_positions)

    cap.release()
    cv2.destroyAllWindows()
    return frame
