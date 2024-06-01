import logging
import cv2
import numpy as np

from env import logging_level
from POC.data_types_POC import Cube, Color, blue_lower, blue_upper, red_lower1, red_upper1, red_lower2, red_upper2, \
    yellow_lower, yellow_upper

global i_frames
i_frames = 0
def detect_colored_cubes(frame, cv2, angle):
    logging.debug(f"----------- getColorOfFrame {angle}-----------")
    blue_contours = detect_contours(frame, blue_lower, blue_upper)
    red_contours = detect_contours(frame, red_lower1, red_upper1, red_lower2, red_upper2)
    # red_contours = detect_contours(frame, red_lower1, red_upper1)
    yellow_contours = detect_contours(frame, yellow_lower, yellow_upper)

    cubes = []

    for cnt in blue_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cube = Cube(Color.BLUE, x, y, w, h)
        if logging_level == logging.DEBUG:
            draw_cube(cnt, cube, cv2, frame)
        cubes.append(cube)

    for cnt in red_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cube = Cube(Color.RED, x, y, w, h)
        if logging_level == logging.DEBUG:
            draw_cube(cnt, cube, cv2, frame)
        cubes.append(cube)

    for cnt in yellow_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cube = Cube(Color.YELLOW, x, y, w, h)
        if logging_level == logging.DEBUG:
            draw_cube(cnt, cube, cv2, frame)
        cubes.append(cube)

    if logging_level == logging.DEBUG:
        global i_frames
        cv2.imwrite(f'test_color_detector_{i_frames}.png', frame)
        i_frames += 1
        # cv2.imshow('Video', frame)
        # while cv2.waitKey(1) & 0xFF != ord('q'):
        #     continue
    return cubes


def detect_contours(image, lower_bound1, upper_bound1, lower_bound2=None, upper_bound2=None, min_area=700):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound1, upper_bound1)
    if lower_bound2 is not None:
        mask = cv2.add(cv2.inRange(hsv, lower_bound2, upper_bound2), mask)

    # Morphologische Operationen
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    mask = cv2.erode(mask, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

    return filtered_contours


def draw_cube(cnt, cube, cv2, frame):
    cv2.rectangle(frame, cube.left_top, cube.right_bottom, cube.color.rgb_value, 2)
    cube.log_values()
    cv2.circle(frame, cube.center, 1, (255, 255, 255), -1)
    cv2.putText(frame, cube.color.color_name, cube.left_top, cv2.FONT_HERSHEY_SIMPLEX, 0.7, cube.color.rgb_value, 2)
    draw_contours(cnt, cv2, frame)


def draw_contours(cnt, cv2, frame):
    epsilon = 0.04 * cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, epsilon, True)
    # logging.debug(approx)
    cv2.drawContours(frame, [approx], -1, (255, 255, 255), 2)
