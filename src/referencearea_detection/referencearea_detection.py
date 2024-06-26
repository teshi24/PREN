import logging
import cv2
import numpy as np

from env import logging_level, show_imgs, write_imgs
from src.camera_interface.camera_interface import open_camera_profile


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


def check_intersection_median(h_line, v_line):
    h_x1, h_y1, h_x2, h_y2 = h_line
    v_x1, v_y1, v_x2, v_y2 = v_line

    # Check if the endpoints of the lines overlap
    if (min(h_x1, h_x2) <= v_x1 <= max(h_x1, h_x2)) and (min(v_y1, v_y2) <= h_y1 <= max(v_y1, v_y2)):
        return calculate_intersection_point(h_line, v_line)
    return False


def calculate_intersection_point(h_line, v_line):
    xdiff = (h_line[0] - h_line[2], v_line[0] - v_line[2])
    ydiff = (h_line[1] - h_line[3], v_line[1] - v_line[3])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        raise ValueError('Lines are parallel and do not intersect')

    d_h = det(h_line[:2], h_line[2:])
    d_v = det(v_line[:2], v_line[2:])
    x = det((d_h, d_v), xdiff) / div
    y = det((d_h, d_v), ydiff) / div
    return int(x), int(y)


def find_frame(frame):
    edges = cv2.Canny(frame, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=150)

    if logging_level == logging.DEBUG:
        frame_copy = frame.copy()

    if lines is not None:
        filtered_lines = []
        horizontal_lines = []
        vertical_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            if np.abs(angle) < 1 or np.abs(angle - 180) < 1:
                if 200 < y1 < 300:
                    filtered_lines.append((line, angle, 'h'))
                    horizontal_lines.append((line, angle))
            elif np.abs(angle - 90) < 1.5 or np.abs(angle + 90) < 1.5:
                if 600 < x1 < 1000:
                    filtered_lines.append((line, angle, 'v'))
                    vertical_lines.append((line, angle))
        # logging.debug(f'filtered_lines: {filtered_lines}')
        # logging.debug(f'horizontal_lines: {horizontal_lines}')
        # logging.debug(f'vertical_lines: {vertical_lines}')

        # Draw the filtered lines in debug mode
        if logging_level == logging.DEBUG:
            for line, angle, _ in filtered_lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(frame_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green lines
                cv2.line(edges, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green lines

        median_horizontal = None
        median_vertical = None
        # get median lines and draw them in debug mode:
        if len(horizontal_lines) > 0:
            median_horizontal = get_median_line(horizontal_lines)
            if logging_level == logging.DEBUG:
                draw_median_line(frame_copy, median_horizontal)
        if len(vertical_lines) > 0:
            median_vertical = get_median_line(vertical_lines)
            if logging_level == logging.DEBUG:
                draw_median_line(frame_copy, median_vertical)

        if show_imgs:
            cv2.imshow('edges', edges)
            cv2.imshow('frame_copy', frame_copy)
            cv2.waitKey(0)

        if median_horizontal is not None and median_vertical is not None:
            intersection_point = check_intersection_median(median_horizontal, median_vertical)
            if intersection_point:
                return frame, intersection_point, edges

    if show_imgs:
        cv2.imshow('edges', edges)
        cv2.imshow('frame_copy', frame_copy)
        cv2.waitKey(0)
    return None, None, None


def draw_median_line(frame_copy, median_line):
    if median_line is not None:
        cv2.line(frame_copy, (int(median_line[0]), int(median_line[1])),
                 (int(median_line[2]), int(median_line[3])), (0, 0, 0), 2)


def get_median_line(lines_with_angles):
    lines = [line[0] for line, _ in lines_with_angles]
    # logging.debug(f'lines {lines}')
    median_line = get_median_without_outliers(5, lines)
    # logging.debug(f'median line {median_line}')
    if np.any(np.isnan(median_line)):
        return None
    return median_line


def get_median_without_outliers(threshold, lines):
    # Calculate the median line length
    line_lengths = np.array([np.linalg.norm(line[2:] - line[:2]) for line in lines])
    median_length = np.median(line_lengths)

    ignore_threshold = len(lines) < 3

    max_length_variance = threshold / 100 * median_length

    # Identify lines as outliers based on their length
    filtered_lines = []
    for line in lines:
        line_length = np.linalg.norm(line[2:] - line[:2])
        # logging.debug(f'line {line}, line_length {line_length}, median_length {median_length}, variance {np.abs(line_length - median_length)}, max_length_var {max_length_variance}')
        if ignore_threshold or np.abs(line_length - median_length) < max_length_variance:
            filtered_lines.append(line)
    # logging.debug(f'filtered lines median calc: {filtered_lines}')

    # Compute the median line (average of filtered_lines)
    median_line = np.mean(filtered_lines, axis=0)
    return median_line


def to_white_area(frame, intersection_point):
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([179, 100, 255])
    contours = detect_contours(frame, lower_white, upper_white)

    # Filter contours by area (adjust the area thresholds as needed)
    min_area = 0
    max_area = 5000000
    largest_contour = None
    largest_area = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if min_area < area < max_area:
            if area > largest_area:
                largest_area = area
                largest_contour = cnt

    # Draw the largest contour on the original image
    if largest_contour is not None:
        if logging_level == logging.DEBUG:
            cv2.drawContours(frame, [largest_contour], 0, (0, 255, 0), 2)
        logging.debug('largest_contour found')
        logging.debug(f'intersection_point {intersection_point}')
        M = cv2.moments(largest_contour)
        if M['m00'] != 0:
            centroid_x = int(M['m10'] / M['m00'])
            centroid_y = int(M['m01'] / M['m00'])
            logging.debug(f"Centroid coordinates: ({centroid_x}, {centroid_y})")
            ref_x = intersection_point[0]
            ref_y = intersection_point[1]
            if centroid_x > ref_x and centroid_y > ref_y:
                return 0
            elif centroid_x > ref_x and centroid_y < ref_y:
                return 270
            elif centroid_y < ref_y:
                return 180
            else:
                return 90
        else:
            logging.debug("Contour area is zero, cannot compute centroid.")
    else:
        logging.debug('no largest contour found')


def get_image_and_angle(frame_queue, running):
    logging.debug('Trying to get image')

    cap = open_camera_profile()

    logging.debug('Image analysis starting...')

    visited_angles = set()
    while running.is_set():
        if len(visited_angles) > 3:
            continue
        ret, frame = cap.read()
        if not ret:
            logging.warning('Warning: unable to read next frame')
            break
        found_frame, intersection_point, edges = find_frame(frame)
        if found_frame is not None:
            angle = to_white_area(found_frame, intersection_point)
            if angle in visited_angles:
                # todo: potentially better handling required
                logging.info(f'angle already visited: {angle}')
                continue

            logging.info(f"Found frame with angle {angle}°")
            frame_queue.put((frame, angle, intersection_point, edges))
            visited_angles.add(angle)
            if write_imgs:
                cv2.imwrite(f'test_frame_angle_{angle}.jpg', frame)
        else:
            # logging.debug("No suitable frame found.")
            pass

    cap.release()



