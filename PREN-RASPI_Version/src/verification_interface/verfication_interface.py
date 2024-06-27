import requests
import json
from datetime import datetime

# Konfigurierbare Parameter
BASE_URL = "https://oawz3wjih1.execute-api.eu-central-1.amazonaws.com"
TEAM_ID = "team28"
AUTH_TOKEN = "Fenz6iYCjkWD"

# Header mit Authentifizierungstoken
headers = {
    "Content-Type": "application/json",
    "Auth": AUTH_TOKEN
}

def start_run():
    url = f"{BASE_URL}/cubes/{TEAM_ID}/start"
    requests.post(url, headers=headers)

def send_config(config_data):
    url = f"{BASE_URL}/cubes/{TEAM_ID}/config"
    requests.post(url, headers=headers, data=json.dumps(config_data))

def end_run():
    url = f"{BASE_URL}/cubes/{TEAM_ID}/end"
    response = requests.post(url, headers=headers)


# Beispiel Konfigurationsdaten
config_data = {
    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "config": {
        "1": "red",
        "2": "blue",
        "3": "red",
        "4": "yellow",
        "5": "",
        "6": "",
        "7": "yellow",
        "8": "red"
    }
}