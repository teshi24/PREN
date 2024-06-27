import logging
import cv2
from typing import Dict, Type

import numpy as np

from .data_types import Color, blue_lower, blue_upper, red_lower1, red_upper1, red_lower2, red_upper2, \
    yellow_lower, yellow_upper

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
# corresponding position in order of positions in frame
position_mapping_0_degrees = [1, 2, 3, 4, 5, 6, 7, 8]
position_mapping_90_degrees = [2, 3, 4, 1, 6, 7, 8, 5]
position_mapping_180_degrees = [3, 4, 1, 2, 7, 8, 5, 6]
position_mapping_270_degrees = [4, 1, 2, 3, 8, 5, 6, 7]


def get_position_mapping_per_angle(angle):
    if angle == 0:
        return position_mapping_0_degrees
    if angle == 90:
        return position_mapping_90_degrees
    if angle == 180:
        return position_mapping_180_degrees
    if angle == 270:
        return position_mapping_270_degrees
    raise ValueError(f'unknown angle provided for gathering the position mapping {angle}')


def log_positions(analysis_name, positions):
    position_string = "{ "
    for key in positions:
        color = positions[key]
        if color is None:
            position_string += str(key) + ": None, "
            continue
        position_string += str(key) + ": " + str(color.color_name) + ", "
    position_string += " }"
    logging.info(analysis_name + " " + position_string)


defaultConfig: Dict[int, Type[Color]] = {
    1: None,
    2: None,
    3: None,
    4: None,
    5: None,
    6: None,
    7: None,
    8: None
}

End_Result = {
    Color.RED.color_name: int,
    Color.BLUE.color_name: int,
    Color.YELLOW.color_name: int,
    Color.NONE.color_name: int
}


def combine_positions(video_positions: [Dict[int, Type[Color]]]):
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


def analyze_frame(frame, angle, intersection_point, edges):
    areas = get_areas(frame)
    positions = find_cube_positions(areas, intersection_point, angle)


    return positions


def find_cube_positions(areas, intersection_point, angle):
    positions = defaultConfig.copy()

    pos_bottom_front_right, pos_bottom_back_right, pos_bottom_back_left, pos_bottom_front_left, pos_top_front_right, pos_top_back_right, pos_top_back_left, pos_top_front_left = get_position_mapping_per_angle(
        angle)

    logging.debug(f'areas unsorted: {areas}')
    top_right, top_left, bottom_left, bottom_right = categorize_areas(areas, intersection_point)

    # todo: handle if this is a problem
    len_bottom_left = len(bottom_left)
    len_bottom_right = len(bottom_right)
    len_top_left = len(top_left)
    len_top_right = len(top_right)
    if len_bottom_left > 1:
        logging.warning(f'Warning: bottom_left has to many values: {len_bottom_left}')
    if len_bottom_right > 1:
        logging.warning(f'Warning: bottom_right has to many values: {len_bottom_right}')
    if len_top_left > 3:
        logging.warning(f'Warning: top_left has to many values: {len_top_left}')
    if len_top_right > 3:
        logging.warning(f'Warning: top_right has to many values: {len_top_right}')

    if len_bottom_left > 0:
        positions[pos_bottom_front_left] = bottom_left[0][-1]
    if len_bottom_right > 0:
        positions[pos_bottom_front_right] = bottom_right[0][-1]
    analyze_top_quarter(positions, len_top_left, top_left, pos_bottom_back_left, pos_bottom_front_left,
                        pos_top_back_left, pos_top_front_left)
    analyze_top_quarter(positions, len_top_right, top_right, pos_bottom_back_right, pos_bottom_front_right,
                        pos_top_back_right, pos_top_front_right)

    log_positions(f'positions at {angle}:', positions)
    return positions


def analyze_top_quarter(positions, len_top_section, top_section, pos_bottom_back, pos_bottom_front, pos_top_back,
                        pos_top_front):
    if len_top_section == 1:  # fallback if the position below has not been found correctly
        if positions[pos_bottom_front] is None:
            positions[pos_bottom_front] = top_section[0][-1]
    elif len_top_section > 1:
        if len_top_section == 3:
            positions[pos_top_back] = top_section[-1][-1]
            del top_section[-1]
        higher_area = top_section[-1]
        lower_area = top_section[0]
        if positions[pos_bottom_front] is None:
            positions[pos_bottom_back] = lower_area[-1]
        else:
            same_color_higher_lower = higher_area[-1] == lower_area[-1]
            if not same_color_higher_lower:
                if positions[pos_top_back] is None:
                    positions[pos_bottom_back] = higher_area[-1]
                # else it is certainly not top front, therefore no new position found
            else:
                if positions[pos_top_back] is None:
                    # compare heights
                    if higher_area[-3] < lower_area[-3]:
                        positions[pos_top_front] = higher_area[-1]
                    else:
                        positions[pos_bottom_back] = higher_area[-1]
                else:
                    if higher_area[-3] < lower_area[-3]:
                        positions[pos_top_front] = higher_area[-1]
                    # else it is certainly not top front, therefore no new position found


def categorize_areas(areas, intersection_point):
    quadrant_I = []
    quadrant_II = []
    quadrant_III = []
    quadrant_IV = []

    for x, y, w, h, center, main_color in areas:
        ## attention - the pixel values for y get bigger if they get lower in the picture, thats why this is inverted
        dx = center[0] - intersection_point[0]
        dy = intersection_point[1] - center[1]

        if dx > 0 and dy > 0:
            quadrant_I.append((x, y, w, h, center, main_color))
        elif dx < 0 and dy > 0:
            quadrant_II.append((x, y, w, h, center, main_color))
        elif dx < 0 and dy < 0:
            quadrant_III.append((x, y, w, h, center, main_color))
        elif dx > 0 and dy < 0:
            quadrant_IV.append((x, y, w, h, center, main_color))

    logging.debug("Quadrant I: %s", quadrant_I)
    logging.debug("Quadrant II: %s", quadrant_II)
    logging.debug("Quadrant III: %s", quadrant_III)
    logging.debug("Quadrant IV: %s", quadrant_IV)

    return quadrant_I, quadrant_II, quadrant_III, quadrant_IV


def get_areas(frame):
    areas = []
    blurred = cv2.GaussianBlur(frame, (3, 3), 0)
    edges_blurred = cv2.Canny(blurred, 20, 180)
    lines = cv2.HoughLinesP(edges_blurred, 1, np.pi / 180, threshold=10, minLineLength=2, maxLineGap=10)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            if np.abs(angle) < 15 or np.abs(angle - 180) < 15:
                cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 0), 3)  # Green lines
            elif np.abs(angle - 90) < 20 or np.abs(angle + 90) < 20:
                cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 0), 3)  # Green lines

    edges_blurred = cv2.Canny(frame, 50, 150)
    lines = cv2.HoughLinesP(edges_blurred, 1, np.pi / 180, threshold=30, minLineLength=1, maxLineGap=80)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            if np.abs(angle) < 5 or np.abs(angle - 180) < 5:
                cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 0), 5)  # Green lines
            elif np.abs(angle - 90) < 5 or np.abs(angle + 90) < 5:
                cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 0), 5)  # Green lines

    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    edges_blurred = cv2.Canny(blurred, 50, 150)
    # # find contours from edges and show them
    contours, _ = cv2.findContours(edges_blurred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_contour_area = 7000
    min_contour_area = 800

    for contour in contours:
        area = cv2.contourArea(contour)
        if min_contour_area < area < max_contour_area:
            x, y, w, h = cv2.boundingRect(contour)
            rectangle_area = w * h
            if min_contour_area < rectangle_area < max_contour_area:
                main_color = get_main_color(frame[y:y + h, x:x + w], x, y)
                if main_color is None:
                    continue
                left_top = (x, y)
                right_bottom = (x + w, y + h)
                cv2.rectangle(frame, left_top, right_bottom, (0, 255, 0), 2)

                center = get_center(contour)
                cv2.circle(frame, center, 3, (0, 255, 0), -1)

                areas.append((x, y, w, h, center, main_color))


    return areas


def get_center(contour):
    M = cv2.moments(contour)
    if M['m00'] != 0:
        centroid_x = int(M['m10'] / M['m00'])
        centroid_y = int(M['m01'] / M['m00'])
        return centroid_x, centroid_y


def get_main_color(rgb_roi, x, y):
    roi = cv2.cvtColor(rgb_roi, cv2.COLOR_BGR2HSV)
    if is_color_matched(roi, red_lower1, red_upper1, red_lower2, red_upper2):
        logging.debug(f"Cube at ({x}, {y}) is red.")
        return Color.RED
    elif is_color_matched(roi, yellow_lower, yellow_upper):
        logging.debug(f"Cube at ({x}, {y}) is yellow.")
        return Color.YELLOW
    elif is_color_matched(roi, blue_lower, blue_upper):
        logging.debug(f"Cube at ({x}, {y}) is blue.")
        return Color.BLUE
    logging.debug(f"Cube at ({x}, {y}) has an unknown color.")
    return None


def is_color_matched(hsv, lower_bound1, upper_bound1, lower_bound2=None, upper_bound2=None):
    mask = cv2.inRange(hsv, lower_bound1, upper_bound1)
    if lower_bound2 is not None:
        mask = cv2.add(cv2.inRange(hsv, lower_bound2, upper_bound2), mask)

    # Morphologische Operationen
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    mask = cv2.erode(mask, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
    return len(contours) > 0