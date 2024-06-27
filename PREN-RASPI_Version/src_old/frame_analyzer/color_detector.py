import logging
import cv2
import numpy as np

from env import logging_level
from .data_types import Cube, Color

# HSV filters
blue_lower = np.array([75, 95, 84])
blue_upper = np.array([145, 255, 255])
red_lower1 = np.array([0, 130, 130])
red_upper1 = np.array([10, 255, 255])
red_lower2 = np.array([170, 70, 50])
red_upper2 = np.array([180, 255, 255])
yellow_lower = np.array([20, 140, 50])
yellow_upper = np.array([50, 255, 255])


def detect_colored_cubes(frame, cv2):
    logging.debug("----------- getColorOfFrame -----------")
    blue_contours = detect_contours(frame, blue_lower, blue_upper)
    red_contours = detect_contours(frame, red_lower1, red_upper1, red_lower2, red_upper2)
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
        cv2.imshow('Video', frame)
        while cv2.waitKey(1) & 0xFF != ord('q'):
            continue
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
    # contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    # Filtern der Konturen nach Fläche
    # ih, iw, ic = image.shape
    # min_area = ih * iw / 400
    # min_area = 500
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
    logging.debug(approx)
    cv2.drawContours(frame, [approx], -1, (255, 255, 255), 2)
