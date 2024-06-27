import logging

import cv2


def open_camera_profile():
    # Open the camera
    username = 'pren'
    password = '463997'
    ip_address = '147.88.48.131'
    profile = 'pren_profile_med'
    cap = setup_video_capture(username, password, ip_address, profile)

    i = 0
    while True:
        logging.debug('tries to open stream')
        if cap is None or not cap.isOpened():
            logging.warning('Warning: Unable to open video source: ', ip_address)
            if i > 10:
                return None
        else:
            break
    return cap

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