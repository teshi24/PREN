import logging
import cv2
import queue
import numpy as np

from env import logging_level
from src.frame_analyzer.color_detector import detect_contours


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
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=50)

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
            elif np.abs(angle - 90) < 1 or np.abs(angle + 90) < 1:
                if 600 < x1 < 800:
                    filtered_lines.append((line, angle, 'v'))
                    vertical_lines.append((line, angle))
        # print(f'filtered_lines: {filtered_lines}')
        # print(f'horizontal_lines: {horizontal_lines}')
        # print(f'vertical_lines: {vertical_lines}')

        # Draw the filtered lines on the original image
        for line, angle, _ in filtered_lines:
            x1, y1, x2, y2 = line[0]
            if logging_level == logging.DEBUG:
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green lines
                cv2.line(edges, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green lines
        median_horizontal = None
        median_vertical = None
        # draw median horizontal / vertical lines:
        if len(horizontal_lines) > 0:
            median_horizontal = draw_median_lines(frame, horizontal_lines)
        if len(vertical_lines) > 0:
            median_vertical = draw_median_lines(frame, vertical_lines)

        if len(horizontal_lines) > 0 and len(vertical_lines) > 0:
            if median_horizontal is not None and median_vertical is not None:
                intersection_point = check_intersection_median(median_horizontal, median_vertical)
                if intersection_point:
                    return frame, intersection_point
                # cv2.imshow('original', frame)
                # # cv2.imshow('edge', edges)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()
    return None, None


def draw_median_lines(frame, lines_with_angles):
    lines = [line[0] for line, _ in lines_with_angles]
    # print(f'lines {lines}')
    median_line = get_median_without_outliers(5, lines)
    # print(f'median line {median_line}')
    if np.any(np.isnan(median_line)):
        return None
    if logging_level == logging.DEBUG:
        cv2.line(frame, (int(median_line[0]), int(median_line[1])),
                 (int(median_line[2]), int(median_line[3])), (0, 0, 255), 2)
    return median_line


def get_median_without_outliers(threshold, lines):
    # Calculate the median line length
    line_lengths = np.array([np.linalg.norm(line[2:] - line[:2]) for line in lines])
    median_length = np.median(line_lengths)

    ignore_threshold = len(lines) < 3

    max_length_variance = threshold / 100 * median_length

    # Identify lines as outliers based on their length
    # filtered_lines = [line for line in lines if np.abs(np.linalg.norm(line[0][2:] - line[0][:2]) - median_length) < threshold]
    filtered_lines = []
    for line in lines:
        line_length = np.linalg.norm(line[2:] - line[:2])
        # print(f'line {line}, line_length {line_length}, median_length {median_length}, variance {np.abs(line_length - median_length)}, max_length_var {max_length_variance}')
        if ignore_threshold or np.abs(line_length - median_length) < max_length_variance:
            filtered_lines.append(line)
    # print(f'filtered lines median calc: {filtered_lines}')
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
        print(f'largest_contour found')
        print(f'intersection_point {intersection_point}')
        M = cv2.moments(largest_contour)
        if M['m00'] != 0:
            centroid_x = int(M['m10'] / M['m00'])
            centroid_y = int(M['m01'] / M['m00'])
            print(f"Centroid coordinates: ({centroid_x}, {centroid_y})")
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
            print("Contour area is zero, cannot compute centroid.")
    else:
        print('no largest contour found')


def get_image_and_angle(frame_queue, running):
    logging.debug('Trying to get image')

    # RTSP-Zugangsdaten und Kameraeinstellungen
    cap = setup_video_capture('pren', '463997', '147.88.48.131', 'pren_profile_med')
    if cap is None or not cap.isOpened():
        logging.warning('Warning: unable to open video source')
        return None

    logging.debug('Image analysis starting...')

    visited_angles = set()
    i = 0
    while running.is_set():
        if len(visited_angles) > 3:
            continue
        ret, frame = cap.read()
        if not ret:
            logging.warning('Warning: unable to read next frame')
            break
        i += 1
        found_frame, intersection_point = find_frame(frame)
        if found_frame is not None:
            angle = to_white_area(found_frame, intersection_point)
            if angle in visited_angles:
                # todo better handling required
                print(f'angle already visited: {angle}')
                continue

            print(f"Found frame with angle {angle}°")
            frame_queue.put((frame, angle))
            visited_angles.add(angle)
            cv2.imwrite(f'test_frame_angle_{angle}_{i}.jpg', frame)
        else:
            print("No suitable frame found.")

    cap.release()


def setup_video_capture(username, password, ip_address, profile):
    """
    Erstellt ein VideoCapture-Objekt für die angegebene RTSP-Quelle.

    :param username: Benutzername für die RTSP-Quelle
    :param password: Passwort für die RTSP-Quelle
    :param ip_address: IP-Adresse der RTSP-Quelle
    :param profile: Streamprofil für die RTSP-Quelle
    :return: VideoCapture-Objekt
    """
    return cv2.VideoCapture('rtsp://' +
                            username + ':' +
                            password +
                            '@' + ip_address +
                            '/axis-media/media.amp' +
                            '?streamprofile=' + profile)
