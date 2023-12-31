from datetime import datetime
import json
import os
from dataclasses import dataclass
from enum import Enum
import cv2
import numpy as np
from typing import Dict, Type, Optional

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
    if (lower_bound2 is not None):
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


class Cube():
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

    def printValues(self):
        print("----------------------")
        print("color: " + self.color.color_name)
        print("x: " + str(self.x))
        print("y: " + str(self.y))
        print("w: " + str(self.w))
        print("h: " + str(self.h))
        print("center       (cx, cy):       " + str(self.center))
        print("left top     (x, y):         " + str(self.left_top))
        print("right top    (x + w, y):     " + str(self.right_top))
        print("right bottom (x + w, y + h): " + str(self.right_bottom))
        print("left bottom  (x, y + h):     " + str(self.left_bottom))

    def width_in_range(self):
        return self.w < cube_max_width

    def height_in_range(self):
        return self.h < cube_max_height


class PositionIdentifier():
    def __init__(self, calibrationCube: Cube, position_in_frame: int, prerequisite: int | None = None, hidden_by: [[int]] = None):
        self.calibrationCube = calibrationCube
        self.toleranceXAxis = 35
        self.toleranceYAxis = 85
        self.position = position_in_frame
        self.prerequisite = prerequisite
        self.hidden_by = hidden_by

    def isCubeAtPosition(self, cube: Cube):
        return (self.__is_value_in_range(cube.x, self.calibrationCube.x, self.toleranceXAxis) and
                self.__is_value_in_range(cube.y, self.calibrationCube.y, self.toleranceYAxis) and
                self.__is_value_in_range(cube.cx, self.calibrationCube.cx, self.toleranceXAxis) and
                self.__is_value_in_range(cube.cy, self.calibrationCube.cy, self.toleranceYAxis))

    def __is_value_in_range(self, value: int, average: int, delta: int):
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

defaultConfig: Dict[int, Type[PositionIdentifier|None]] = {
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

def splitCubesNextToEachOther(cube: [Cube]):
    half_w = int(cube.w / 2)

    right_cube = Cube(cube.color, cube.x, cube.y, half_w, cube.h)
    left_cube = Cube(cube.color, cube.x + half_w, cube.y, half_w, cube.h)

    return [right_cube, left_cube]

def splitCubesOnTopOfEachOther(cube: [Cube]):
    half_h = int(cube.h / 2)

    right_cube = Cube(cube.color, cube.x, cube.y, cube.w, half_h)
    left_cube = Cube(cube.color, cube.x, cube.y + half_h, cube.w, half_h)

    return [right_cube, left_cube]


def splitBigCubes(cubes: [Cube]):
    cleanCubes: [Cube] = []

    for cube in cubes:
        width_in_range = cube.width_in_range()
        height_in_range = cube.height_in_range()
        if width_in_range and height_in_range:
            # cube standardsize
            cleanCubes.append(cube)
            continue
        if not width_in_range:
            if not height_in_range:
                # todo: fix spezialfall - mit cnts analysieren
                cleanCubes.append(cube)
                continue
            # nebeneinander
            cleanCubes.extend(splitCubesNextToEachOther(cube))
            continue
        # todo: fix spezialfall wahrscheinlich obereinander
        #       ! kann aber auch hintereinander sein !
        cleanCubes.extend(splitCubesOnTopOfEachOther(cube))

    return cleanCubes


def analyzePositionsInOneFrame(cubes: [Cube], angle):
    positions = defaultConfig.copy()

    calibratedPositions = CalibratedPositions.from_angle(angle).positions

    for cube in cubes:
        print("color: " + str(cube.color.color_name) + ", x: " + str(cube.x) + ", y: " + str(cube.y) + ", center: " + str(cube.center))
        for key, position_identifier in calibratedPositions.items():
            print("calibratedPosition: " + str(position_identifier))
            if positions[key] is None and position_identifier is not None and position_identifier.isCubeAtPosition(cube):
                positions[key] = cube.color
                break

    print_positions("detected positions:", positions)

    # todo: fix prep
    # changed_positions = positions.copy()
    # for key in positions:
    #     color = positions[key]
    #     if color is None:
    #         continue
    #     calibratedPosition = calibratedPositions[key]
    #     print("analyzed item: " + str(key) + ': ' + str(positions[key]))
    #     if calibratedPosition is not None and calibratedPosition.prerequisite is not None: # and calibratedPosition.prerequisite is not None:
    #         print("calibration item as prerequisite: " + str(calibratedPosition.prerequisite) + ': ' + str(positions[calibratedPosition.prerequisite]))
    #         if positions[calibratedPosition.prerequisite] is not None:
    #             print("issue detected - invisible item was detected as a color; value set to None")
    #             changed_positions[key] = None
    #
    # print_positions("positions after changes:", changed_positions)
    return positions

def print_positions(analysis_name, positions):
    print(analysis_name)
    positionString = "{ "
    for key in positions:
        color = positions[key]
        if color is None:
            positionString += str(key) + ": None,"
            continue
        positionString += str(key) + ": " + str(color.color_name) + ","
    positionString += " }"
    print(positionString)


def getCubesFromFrame(frame, angle, cv2):
    print("----------- getColorOfFrame -----------")
    blue_contours = detect_color(frame, blue_lower, blue_upper)
    red_contours = detect_color(frame, red_lower1, red_upper1, red_lower2, red_upper2)
    yellow_contours = detect_color(frame, yellow_lower, yellow_upper)

    cubes = []

    for cnt in blue_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cube = Cube(Color.BLUE, x, y, w, h)
        cv2 = drawCube(cnt, cube, cv2, frame)
        cubes.append(cube)

    for cnt in red_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cube = Cube(Color.RED, x, y, w, h)
        cv2 = drawCube(cnt, cube, cv2, frame)
        cubes.append(cube)

    for cnt in yellow_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cube = Cube(Color.YELLOW, x, y, w, h)
        cv2 = drawCube(cnt, cube, cv2, frame)
        cubes.append(cube)

    cv2.imshow('Video', frame)
    while (cv2.waitKey(1) & 0xFF != ord('q')):
        continue
    return [cv2, cubes]


def drawCube(cnt, cube, cv2, frame):
    cv2.rectangle(frame, cube.left_top, cube.right_bottom, cube.color.rgb_value, 2)
    cube.printValues()
    cv2.circle(frame, cube.center, 1, (255, 255, 255), -1)
    cv2.putText(frame, cube.color.color_name, cube.left_top, cv2.FONT_HERSHEY_SIMPLEX, 0.7, cube.color.rgb_value, 2)
    drawContours(cnt, cv2, frame)
    return cv2


def drawContours(cnt, cv2, frame):
    epsilon = 0.04 * cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, epsilon, True)
    print(approx)
    cv2.drawContours(frame, [approx], -1, (255, 255, 255), 2)


End_Result = {
    Color.RED.color_name: int,
    Color.BLUE.color_name: int,
    Color.YELLOW.color_name: int,
    Color.NONE.color_name: int
}

def analyze_video_positions(video_positions: [Dict[int, Type[PositionIdentifier|None]]]):
    print("analyze_video_positions started")
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
            print('positions was None')
            continue
        print('positions: ' + str(positions))
        for key, color in positions.items():
            if key is None:
                print('key was None')
                continue
            if color is None:
                print('color was None')
                continue
            print('key: ' + str(key))
            print('color: ' + str(color))
            print('color.color_name' + str(color.color_name))
            print('end_positions_percentages[key]: ' + str(end_positions_percentages[key]))
            print('end_positions_percentages[key][color.color_name]: ' + str(end_positions_percentages[key][color.color_name]))
            end_positions_percentages[key][color.color_name] += 25

    print("end result percentages")
    for end_position, colors in end_positions_percentages.items():
        print(str(end_position) + ": " + str(colors))

    end_result = defaultConfig.copy()
    print("end result")
    for end_position, colors in end_positions_percentages.items():
        most_probable_color = max(colors, key=colors.get)

        # Check if there are duplicates with the same highest value
        if list(colors.values()).count(colors[most_probable_color]) > 1:
            end_result[end_position] = ''
        else:
            end_result[end_position] = most_probable_color
    print(end_result)
    now = datetime.now().strftime('%Y-%m-%d.%H.%M.%S')
    file_name = 'end_result_' + str(now) + '.json'
    file_path = os.path.join('testdata', file_name)
    with open(file_path, 'w') as file:
        json.dump(end_result, file)


def analyze_cube_video(PATH):
    # VideoCapture-Objekt erstellen und Video-Datei laden
    cap = cv2.VideoCapture(PATH)

    frameCount = 0
    angle = 0
    video_positions: [Dict[int, Type[PositionIdentifier|None]]] = []
    while True:
        if angle > 270:
            break

        ret, frame = cap.read()
        if not ret:
            break

        if frameCount != 0:
            frameCount = frameCount - 1
            continue
        else:
            # todo: check with angle detector whether we are good
            frameCount = 220

        [cv3, raw_cubes] = getCubesFromFrame(frame, angle, cv2)
        cubes = splitBigCubes(raw_cubes)
        video_positions.append(analyzePositionsInOneFrame(cubes, angle))

        angle = angle + 90
        # if angle >= 270:
        # todo: remove
        break
    analyze_video_positions(video_positions)

    return frame
    cap.release()
    cv2.destroyAllWindows()
