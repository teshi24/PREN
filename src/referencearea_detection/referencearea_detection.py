import logging
import math
from queue import Queue
from threading import Event

import cv2
import numpy as np

allowed_angles = [0, 39, 40, 41, 42, 43, 44, 45, 135, 225, 315]
allowed_angles = [0, 39, 40, 41, 42, 43, 44, 45, 135, 225, 315]


def find_centeroid_white(image):
    # Convert image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define range of white color in HSV
    # These values can be adjusted to be more specific for the white color in the images
    lower_white = np.array([0, 0, 168], dtype=np.uint8)
    upper_white = np.array([172, 111, 255], dtype=np.uint8)

    # Threshold the HSV image to get only white colors
    mask = cv2.inRange(hsv, lower_white, upper_white)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter out very small contours that are unlikely to be the white area
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 100]


    # Assuming the largest contour is the white area
    largest_contour = max(contours, key=cv2.contourArea)

    # Compute the centroid of the largest contour
    moments = cv2.moments(largest_contour)
    if moments['m00'] != 0:
        cx = int(moments['m10'] / moments['m00'])  # cx = M10/M00
        cy = int(moments['m01'] / moments['m00'])  # cy = M01/M00
    else:
        # Set centroid to the center of the image if contour is not found
        cx, cy = image.shape[1] // 2, image.shape[0] // 2

    return cx, cy,


def calculate_angle(frame):
    pt1 = find_centeroid_white(frame)
    pt2 = 641, 277  # TODO Dynamic or Config File

    # Calculate the difference between the two points
    delta_x = pt2[0] - pt1[0]
    delta_y = pt2[1] - pt1[1]

    # Calculate the angle in radians and then convert to degrees
    angle_radians = math.atan2(delta_y, delta_x)
    angle_degrees = math.degrees(angle_radians)

    return int(angle_degrees) + 180


def get_image_and_angle(result_queue: Queue, running: Event):
    logging.debug('trying to get image')

    username = 'pren'
    password = '463997'
    ip_address = '147.88.48.131'
    profile = 'pren_profile_med'
    cap = cv2.VideoCapture('rtsp://' +
                           username + ':' +
                           password +
                           '@' + ip_address +
                           '/axis-media/media.amp' +
                           '?streamprofile=' + profile)
    if cap is None or not cap.isOpened():
        logging.warning('Warning: unable to open video source: ', ip_address)
        return None

    logging.debug('image analysis starting...')
    i = 0
    last_angle = None
    while running.is_set():
        ret, frame = cap.read()
        if not ret:
            logging.warning('Warning: unable to read next frame')
            break

        i += 1
        cv2.imwrite(f'test_frame_{i}.jpg', frame)

        logging.debug('angle calculating...')
        angle = calculate_angle(frame)
        logging.debug('angle calculated')
        if angle is last_angle:
            logging.warning('Warning: still the same frame according to angle')
            # todo: this is wrong, it saved a different frame everytime
            continue
        last_angle = angle
        if angle not in allowed_angles:
            logging.warning(f'Warning: angle ({angle}) not in allowed range')
            continue

        logging.debug(f'angle was ok {angle}')
        result_queue.put((frame, angle))
