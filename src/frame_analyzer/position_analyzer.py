import logging
from dataclasses import dataclass
from enum import Enum
import cv2
from typing import Dict, Type
from .color_detector import detect_colored_cubes
from .data_types import Cube, Color


class PositionIdentifier:
    def __init__(self,
                 calibration_cube: Cube,
                 position_in_frame: int,
                 prerequisite: int | None = None,
                 hidden_by: [[int]] = None):
        self.calibrationCube = calibration_cube
        # todo: check tolerances
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

# difference for 8  top front left        242,    057,    090,    165
# difference for 5  top front right       322,    065,    100,    114
# difference for 7  top back  left        240,    011,    081,   -091
# difference for 6  top back  right       316,    034,    092,    070
# difference for 3  bottom back left      241,    184,    086,    066
# difference for 2  bottom back right     320,    184,    086,    066
# difference for 1  bottom front right    323,    215,    072,    020
# difference for 4  bottom front left     241,    152,    079,    079

# --> left                              ca. 241
# --> right                             ca. 320
# --> top                                       ca. 042
# --> bottom                                    ca. 184
# --> avg                                               ca. 86  ca. 66

# extra sortiert, damit andere Reihenfolge entdeckt wird
# when analyzing from videos
# calibratedPositions0Degree = {
#     8: PositionIdentifier(Cube(Color.NONE, 770, 177, 200, 274), 8, 4),
#     5: PositionIdentifier(Cube(Color.NONE, 964, 183, 210, 258), 5, 1),
#     7: PositionIdentifier(Cube(Color.NONE, 780, 98, 186, 126), 7, 3),
#     6: PositionIdentifier(Cube(Color.NONE, 952, 100, 196, 100), 6, 2),
#     3: None,  # PositionIdentifier(Cube(Color.NONE, 967, 411, 196, 100)),
#     2: PositionIdentifier(Cube(Color.NONE, 968, 244, 164, 98), 2),
#     1: PositionIdentifier(Cube(Color.NONE, 967, 411, 182, 162), 1),
#     4: PositionIdentifier(Cube(Color.NONE, 781, 416, 184, 158), 4),
# }


# todo: further calibrate, especially position 2
# extra sortiert, damit andere Reihenfolge entdeckt wird
calibratedPositions0Degree = {
    8: PositionIdentifier(Cube(Color.NONE, 532, 120, 110, 109), 8, 4),
    # difference for 8                        242,    057,    090,    165
    5: PositionIdentifier(Cube(Color.NONE, 642, 118, 110, 144), 5, 1),
    # difference for 5                        322,    065,    100,    114
    7: PositionIdentifier(Cube(Color.NONE, 540, 87, 105, 135), 7, 3),
    # difference for 7                        240,    011,    081,   -091
    6: PositionIdentifier(Cube(Color.NONE, 636, 66, 104, 130), 6, 2),
    # difference for 6                        316,    034,    092,    070
    3: None,  # PositionIdentifier(Cube(Color.NONE, 728, 227, 110, 034)),
    # difference for 3  bottom back left            241, 184, 086, 066
#   2: PositionIdentifier(Cube(Color.NONE, 968, 244, 164, 98), 2),
    2: PositionIdentifier(Cube(Color.NONE, 648, 100, 90, 32), 2),
    # difference for 2  bottom back right     320,    184,    086,    066
    1: PositionIdentifier(Cube(Color.NONE, 644, 196, 110, 142), 1),
    # difference for 1                        323,    215,    072,    020
    4: PositionIdentifier(Cube(Color.NONE, 540, 264, 105, 79), 4),
    # difference for 4                        241,    152,    079,    079
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

    # todo: cleanup angle
    @classmethod
    def from_angle(cls, angle):
        if angle == 0 or angle == 45:
            return cls.DEGREE_0
        elif angle == 90 or angle == 135:
            return cls.DEGREE_90
        elif angle == 180 or angle == 225:
            return cls.DEGREE_180
        elif angle == 270 or angle == 315:
            return cls.DEGREE_270
        else:
            raise ValueError(f"Invalid angle: {angle}")


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
        logging.debug('color: %s, x: %d, y: %d, center: %s', cube.color.color_name, cube.x, cube.y, cube.center)
        for key, position_identifier in calibrated_positions.items():
            if positions[key] is None and position_identifier is not None and position_identifier.is_cube_at_position(
                    cube):
                positions[key] = cube.color
                break

    log_positions(f"detected positions for {angle}:", positions)
    return positions


def log_positions(analysis_name, positions):
    position_string = "{ "
    for key in positions:
        color = positions[key]
        if color is None:
            position_string += str(key) + ": None,"
            continue
        position_string += str(key) + ": " + str(color.color_name) + ","
    position_string += " }"
    logging.info(analysis_name + position_string)


End_Result = {
    Color.RED.color_name: int,
    Color.BLUE.color_name: int,
    Color.YELLOW.color_name: int,
    Color.NONE.color_name: int
}


def combine_positions(video_positions: [Dict[int, Type[PositionIdentifier | None]]]):
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
        logging.debug('positions: %s', positions)
        for key, color in positions.items():
            if key is None:
                logging.debug('key was None')
                continue
            if color is None:
                logging.debug('color was None')
                continue
            logging.debug('key: %s', key)
            logging.debug('color: %s', color)
            logging.debug('color.color_name: %s', color.color_name)
            logging.debug('end_positions_percentages[key]: %s', end_positions_percentages[key])
            logging.debug('end_positions_percentages[key][color.color_name]: %s',
                          end_positions_percentages[key][color.color_name])
            end_positions_percentages[key][color.color_name] += 25

    logging.debug("end result percentages")
    for end_position, colors in end_positions_percentages.items():
        logging.debug('%d: %s', end_position, colors)

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
    return end_result


def analyze_frame(frame, angle):
    raw_cubes = detect_colored_cubes(frame, cv2, angle)
    cubes = split_big_cubes(raw_cubes)
    return analyze_positions_in_one_frame(cubes, angle)
