import cv2


def open_camera_profile():
# Open the camera
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
        print('Warning: unable to open video source: ', ip_address)
        return None
    while True:
        ret, frame = cap.read()
        if not ret:
            print('Warning: unable to read next frame')
            break
        return frame
