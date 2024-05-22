import logging
import cv2
import queue

# Weisser Farbbereich in BGR
color_range = ((190, 190, 190), (255, 255, 255))
def get_image_and_angle(frame_queue):
    """
    Funktion, um ein Bild von einer RTSP-Quelle zu erhalten und die Koordinaten
    auf das Vorhandensein bestimmter Farben zu überprüfen. Wenn eine passende
    Farbe gefunden wird, wird das entsprechende Frame und der Name des Koordinatensets
    in eine Queue geschrieben.

    :param frame_queue: Queue zum Speichern von Frames und den zugehörigen Namen
    """
    logging.debug('Trying to get image')

    # RTSP-Zugangsdaten und Kameraeinstellungen
    cap = setup_video_capture('pren', '463997', '147.88.48.131', 'pren_profile_med')
    if cap is None or not cap.isOpened():
        logging.warning('Warning: unable to open video source')
        return None

    logging.debug('Image analysis starting...')

    coordinate_sets = get_coordinate_sets()
    checked_sets = set()  # Set zur Verfolgung der bereits überprüften Koordinatensets

    while True:
        ret, frame = cap.read()
        if not ret:
            logging.warning('Warning: unable to read next frame')
            break

        for coordinates, name in coordinate_sets:
            if name not in checked_sets:
                results = check_coordinates_in_color_range(frame, coordinates, color_range)
                print(f"Results for {name}: {results}")

                if all(results):
                    frame_queue.put((frame, name))
                    checked_sets.add(name)
                    break

        if len(checked_sets) == len(coordinate_sets):
            break


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


def get_coordinate_sets():
    """
    Gibt die Liste der Koordinatensets und ihre Namen zurück.

    :return: Liste der Koordinatensets und ihre Namen
    """
    coordinatesur = [(753, 261), (970, 260), (753, 91)]
    coordinatesul = [(550, 84), (434, 260), (326, 260), (544,203)] #TODO koordinaten hinzufügen für bessere präzision
    coordinatesdr = [(655, 333), (655, 533), (846, 272)]
    coordinatesdl = [(330, 261), (500, 261), (542,150)]
    return [
        (coordinatesul, "315"),
        (coordinatesur, "45"),
        (coordinatesdl, "135"),
        (coordinatesdr, "225")
    ]


def is_color_in_range(color, color_range):
    """
    Überprüft, ob eine Farbe innerhalb eines bestimmten Farbbereichs liegt.

    :param color: Ein Tupel (B, G, R) der Farbe
    :param color_range: Ein Tupel ((B_min, G_min, R_min), (B_max, G_max, R_max))
    :return: True, wenn die Farbe im Bereich liegt, sonst False
    """
    (B, G, R) = color
    (B_min, G_min, R_min), (B_max, G_max, R_max) = color_range
    return B_min <= B <= B_max and G_min <= G_max and R_min <= R_max


def check_coordinates_in_color_range(image, coordinates, color_range):
    """
    Überprüft, ob die Farben an den gegebenen Koordinaten innerhalb eines Farbbereichs liegen.

    :param image: Eingabebild
    :param coordinates: Liste von Koordinaten (x, y)
    :param color_range: Ein Tupel ((B_min, G_min, R_min), (B_max, G_max, R_max))
    :return: Liste von bools, die angeben, ob die Farbe an jeder Koordinate im Bereich liegt
    """
    results = []
    for coord in coordinates:
        x, y = coord
        color = image[y, x]
        in_range = is_color_in_range(color, color_range)
        results.append(in_range)

    return results



